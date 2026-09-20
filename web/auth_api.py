from __future__ import annotations

import hashlib
import os
from urllib.parse import urlparse

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from shared.auth_db import (
    create_session,
    create_user,
    delete_all_sessions,
    delete_session,
    get_user_by_email,
    get_user_by_google_sub,
    get_user_by_id,
    get_user_by_session,
    hash_password,
    init_db,
    normalize_email,
    update_login,
    update_user,
    verify_password,
    validate_password,
)

router = APIRouter(prefix="/api", tags=["auth"])
SESSION_COOKIE = "gm_session"
COOKIE_MAX_AGE = 30 * 24 * 60 * 60
SUPPORTED_LANGUAGES = {
    "id", "en", "ms", "ar", "ja", "ko", "zh", "es", "pt", "fr"
}
SUPPORTED_THEMES = {"light", "dark", "system"}

oauth = OAuth()
GOOGLE_CONFIGURED = bool(
    os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET")
)

if GOOGLE_CONFIGURED:
    oauth.register(
        name="google",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class RegisterRequest(Credentials):
    name: str = Field(min_length=2, max_length=100)
    language: str = Field(default="id", min_length=2, max_length=5)


class SettingsRequest(BaseModel):
    language: str = Field(min_length=2, max_length=5)
    theme: str = Field(min_length=4, max_length=10)
    notifications: bool = True


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


def _public_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "avatar_url": user.get("avatar_url"),
        "language": user.get("language", "id"),
        "theme": user.get("theme", "light"),
        "notifications": bool(user.get("notifications", 1)),
        "email_verified": bool(user.get("email_verified", 0)),
        "created_at": user.get("created_at"),
        "last_login_at": user.get("last_login_at"),
        "has_password": bool(user.get("password_hash")),
        "google_connected": bool(user.get("google_sub")),
    }


def _same_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if not origin:
        return
    parsed_origin = urlparse(origin)
    host = request.headers.get("host", "")
    if parsed_origin.netloc != host:
        raise HTTPException(status_code=403, detail="Origin tidak diizinkan.")


def current_user(request: Request) -> dict:
    token = request.cookies.get(SESSION_COOKIE)
    user = get_user_by_session(token or "")
    if user is None:
        raise HTTPException(status_code=401, detail="Login diperlukan.")
    return user


def _set_session(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "0") == "1",
        samesite="lax",
        path="/",
    )


def _clear_session(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")


@router.get("/auth/status")
def auth_status():
    return {
        "google_enabled": GOOGLE_CONFIGURED,
        "languages": sorted(SUPPORTED_LANGUAGES),
        "themes": sorted(SUPPORTED_THEMES),
    }


@router.get("/auth/me")
def me(user: dict = Depends(current_user)):
    return _public_user(user)


@router.post("/auth/register")
def register(request: Request, payload: RegisterRequest, response: Response):
    _same_origin(request)
    init_db()

    if payload.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Bahasa tidak didukung.")

    try:
        email = normalize_email(payload.email)
        validate_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if get_user_by_email(email):
        raise HTTPException(status_code=409, detail="Email sudah terdaftar.")

    try:
        user_id = create_user(
            email,
            payload.name,
            payload.password,
            language=payload.language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    token = create_session(user_id)
    _set_session(response, token)
    user = get_user_by_id(user_id)
    assert user is not None
    return {"user": _public_user(user)}


@router.post("/auth/login")
def login(request: Request, payload: Credentials, response: Response):
    _same_origin(request)
    init_db()

    try:
        email = normalize_email(payload.email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = get_user_by_email(email)
    if (
        user is None
        or not user.get("password_hash")
        or not user.get("password_salt")
        or not verify_password(
            payload.password,
            user["password_salt"],
            user["password_hash"],
        )
    ):
        raise HTTPException(status_code=401, detail="Email atau password salah.")

    update_login(user["id"])
    token = create_session(user["id"])
    _set_session(response, token)
    user = get_user_by_id(user["id"])
    assert user is not None
    return {"user": _public_user(user)}


@router.post("/auth/logout")
def logout(request: Request, response: Response):
    _same_origin(request)
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        delete_session(token)
    _clear_session(response)
    return {"ok": True}


@router.post("/auth/logout-all")
def logout_all(request: Request, response: Response, user: dict = Depends(current_user)):
    _same_origin(request)
    delete_all_sessions(user["id"])
    _clear_session(response)
    return {"ok": True}


@router.put("/auth/settings")
def settings(
    request: Request,
    payload: SettingsRequest,
    user: dict = Depends(current_user),
):
    _same_origin(request)
    if payload.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Bahasa tidak didukung.")
    if payload.theme not in SUPPORTED_THEMES:
        raise HTTPException(status_code=400, detail="Tema tidak didukung.")
    updated = update_user(
        user["id"],
        language=payload.language,
        theme=payload.theme,
        notifications=1 if payload.notifications else 0,
    )
    return {"user": _public_user(updated)}


@router.put("/auth/password")
def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    user: dict = Depends(current_user),
):
    _same_origin(request)
    if not user.get("password_hash") or not user.get("password_salt"):
        raise HTTPException(
            status_code=400,
            detail="Akun ini belum memiliki password lokal.",
        )
    if not verify_password(
        payload.current_password,
        user["password_salt"],
        user["password_hash"],
    ):
        raise HTTPException(status_code=401, detail="Password lama salah.")

    try:
        salt_hex, password_hash = hash_password(payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    update_user(
        user["id"],
        password_hash=password_hash,
        password_salt=salt_hex,
    )
    return {"ok": True}


@router.get("/auth/google/start", name="google_start")
async def google_start(request: Request):
    if not GOOGLE_CONFIGURED:
        raise HTTPException(
            status_code=503,
            detail="Google Login belum dikonfigurasi. Isi GOOGLE_CLIENT_ID dan GOOGLE_CLIENT_SECRET.",
        )

    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    if not redirect_uri:
        redirect_uri = str(request.url_for("google_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback", name="google_callback")
async def google_callback(request: Request, response: Response):
    if not GOOGLE_CONFIGURED:
        raise HTTPException(status_code=503, detail="Google Login belum dikonfigurasi.")

    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get("userinfo")
        if not userinfo:
            userinfo = await oauth.google.userinfo(token=token)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Google Login gagal: {exc}",
        ) from exc

    google_sub = str(userinfo.get("sub", "")).strip()
    email = str(userinfo.get("email", "")).strip().lower()
    name = str(userinfo.get("name") or email.split("@", 1)[0]).strip()
    avatar = str(userinfo.get("picture") or "").strip() or None
    verified = bool(userinfo.get("email_verified"))

    if not google_sub or not email:
        raise HTTPException(
            status_code=400,
            detail="Google tidak mengembalikan identitas email yang valid.",
        )

    user = get_user_by_google_sub(google_sub)
    if user is None:
        existing = get_user_by_email(email)
        if existing:
            user = update_user(
                existing["id"],
                google_sub=google_sub,
                avatar_url=avatar,
                email_verified=1 if verified else 0,
            )
        else:
            user_id = create_user(
                email,
                name,
                None,
                google_sub=google_sub,
                avatar_url=avatar,
            )
            user = get_user_by_id(user_id)
            assert user is not None
            if verified:
                user = update_user(user_id, email_verified=1)

    update_login(user["id"])
    token_value = create_session(user["id"])
    _set_session(response, token_value)

    return Response(
        content='<script>window.location.replace("/#account");</script>',
        media_type="text/html",
        headers={"Cache-Control": "no-store"},
    )
