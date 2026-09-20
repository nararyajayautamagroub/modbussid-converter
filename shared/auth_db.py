from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "data" / "app.db"
PBKDF2_ITERATIONS = 600_000
SESSION_DAYS = 30


def _db_path() -> Path:
    raw = os.getenv("GAME_MOD_DB")
    path = Path(raw).expanduser() if raw else DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                name TEXT NOT NULL,
                password_hash TEXT,
                password_salt TEXT,
                google_sub TEXT UNIQUE,
                avatar_url TEXT,
                language TEXT NOT NULL DEFAULT 'id',
                theme TEXT NOT NULL DEFAULT 'light',
                notifications INTEGER NOT NULL DEFAULT 1,
                email_verified INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                last_login_at TEXT
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_user
            ON sessions(user_id);

            CREATE INDEX IF NOT EXISTS idx_sessions_expiry
            ON sessions(expires_at);
            """
        )
        conn.execute(
            "DELETE FROM sessions WHERE expires_at <= ?",
            (_utc_now(),),
        )


def normalize_email(email: str) -> str:
    value = email.strip().lower()
    if len(value) > 254 or "@" not in value or value.startswith("@") or value.endswith("@"):
        raise ValueError("Email tidak valid.")
    local, domain = value.rsplit("@", 1)
    if not local or "." not in domain:
        raise ValueError("Email tidak valid.")
    return value


def validate_password(password: str) -> None:
    if not 8 <= len(password) <= 128:
        raise ValueError("Password harus 8-128 karakter.")
    if password.lower() == password or password.upper() == password:
        raise ValueError("Password harus memiliki huruf besar dan kecil.")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password harus memiliki minimal satu angka.")


def hash_password(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    validate_password(password)
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return salt.hex(), digest.hex()


def verify_password(password: str, salt_hex: str, expected_hash: str) -> bool:
    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        PBKDF2_ITERATIONS,
    ).hex()
    return secrets.compare_digest(candidate, expected_hash)


def create_user(
    email: str,
    name: str,
    password: str | None = None,
    *,
    google_sub: str | None = None,
    avatar_url: str | None = None,
    language: str = "id",
) -> int:
    email = normalize_email(email)
    name = " ".join(name.strip().split())[:100] or email.split("@", 1)[0][:100]
    salt_hex = password_hash = None
    if password is not None:
        salt_hex, password_hash = hash_password(password)

    with connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users
            (email,name,password_hash,password_salt,google_sub,avatar_url,
             language,created_at)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                email,
                name,
                password_hash,
                salt_hex,
                google_sub,
                avatar_url,
                language,
                _utc_now(),
            ),
        )
        return int(cursor.lastrowid)


def get_user_by_id(user_id: int) -> dict | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_email(email: str) -> dict | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (normalize_email(email),),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_google_sub(google_sub: str) -> dict | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE google_sub = ?",
            (google_sub,),
        ).fetchone()
    return dict(row) if row else None


def update_login(user_id: int) -> None:
    with connection() as conn:
        conn.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (_utc_now(), user_id),
        )


def update_user(user_id: int, **fields) -> dict:
    allowed = {
        "name",
        "google_sub",
        "avatar_url",
        "language",
        "theme",
        "notifications",
        "email_verified",
        "password_hash",
        "password_salt",
    }
    values = {key: value for key, value in fields.items() if key in allowed}
    if not values:
        user = get_user_by_id(user_id)
        if user is None:
            raise ValueError("User tidak ditemukan.")
        return user

    assignments = ", ".join(f"{key} = ?" for key in values)
    params = list(values.values()) + [user_id]
    with connection() as conn:
        conn.execute(
            f"UPDATE users SET {assignments} WHERE id = ?",
            params,
        )
    return get_user_by_id(user_id)  # type: ignore[return-value]


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    from datetime import timedelta

    created = datetime.now(timezone.utc)
    expires = created + timedelta(days=SESSION_DAYS)
    with connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions(token_hash,user_id,created_at,expires_at)
            VALUES(?,?,?,?)
            """,
            (
                token_hash,
                user_id,
                created.isoformat(),
                expires.isoformat(),
            ),
        )
    return token


def get_user_by_session(token: str) -> dict | None:
    if not token:
        return None
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = _utc_now()
    with connection() as conn:
        row = conn.execute(
            """
            SELECT u.*
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = ? AND s.expires_at > ?
            """,
            (token_hash, now),
        ).fetchone()
        conn.execute(
            "DELETE FROM sessions WHERE expires_at <= ?",
            (now,),
        )
    return dict(row) if row else None


def delete_session(token: str) -> None:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connection() as conn:
        conn.execute(
            "DELETE FROM sessions WHERE token_hash = ?",
            (token_hash,),
        )


def delete_all_sessions(user_id: int) -> None:
    with connection() as conn:
        conn.execute(
            "DELETE FROM sessions WHERE user_id = ?",
            (user_id,),
        )
