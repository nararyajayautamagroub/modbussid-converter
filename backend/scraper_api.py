from __future__ import annotations

from fastapi import APIRouter, HTTPException

from core.scraper import crawl_site, scrape_page

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


@router.get("/fetch")
def fetch(
    url: str,
    max_bytes: int = 5 * 1024 * 1024,
    max_links: int = 100,
    timeout: int = 10,
):
    try:
        return scrape_page(
            url,
            max_bytes=max_bytes,
            max_links=max_links,
            timeout=timeout,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/crawl")
def crawl(
    url: str,
    max_pages: int = 10,
    max_links_per_page: int = 50,
    max_bytes: int = 5 * 1024 * 1024,
    timeout: int = 10,
):
    try:
        return crawl_site(
            url,
            max_pages=max_pages,
            max_links_per_page=max_links_per_page,
            max_bytes=max_bytes,
            timeout=timeout,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
