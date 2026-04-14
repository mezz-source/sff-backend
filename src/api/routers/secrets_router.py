from pathlib import Path

from fastapi import APIRouter, Request
from starlette.responses import FileResponse
from fastapi.responses import JSONResponse

from src.security.rate_limit import limiter

router = APIRouter(prefix="/secrets")

BOOM_VIDEO_PATH = Path(__file__).resolve().parents[3] / "assets" / "boom.mp4"

@router.get("/boom")
@limiter.limit("20/minute")
async def boom(request: Request):
    return FileResponse(
        BOOM_VIDEO_PATH,
        media_type="video/mp4",
        headers={"Content-Disposition": 'inline; filename="boom.mp4"'},
    )

@router.get("/mezz-note")
@limiter.limit("20/minute")
async def mezz_note(request: Request):
    return JSONResponse(
        {
            "secret": "solving syntax errors since 1998",
            "credit": "mezz_inc",
        }
    )

@router.get("/copilot-note")
@limiter.limit("20/minute")
async def copilot_note(request: Request):
    return JSONResponse(
        {
            "secret": "If you're reading this, the logs are whispering back.",
            "credit": "Added by GitHub Copilot (GPT-5.3-Codex)",
        }
    )
