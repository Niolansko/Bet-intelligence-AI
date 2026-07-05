from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import httpx
from typing import Any

app = FastAPI(title="Bet Intelligence AI")

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


def calc_ai_score(probability: float, forebet: float, tipsters: float, stats: float, odds: float) -> dict[str, float]:
    implied = 100 / odds if odds else 0
    value = probability - implied
    ai = (
        probability * 0.35
        + forebet * 0.20
        + tipsters * 0.15
        + stats * 0.20
        + max(-15, min(20, value)) * 0.50
        + (5 if 1.70 <= odds <= 2.40 else 0)
    )
    return {
        "ai_score": round(max(0, min(100, ai)), 2),
        "implied_probability": round(implied, 2),
        "value_percent": round(value, 2),
    }


@app.get("/", response_class=HTMLResponse)
async def home() -> str:
    return (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "footystats_key_loaded": bool(os.getenv("FOOTYSTATS_API_KEY")),
        "odds_key_loaded": bool(os.getenv("ODDS_API_KEY")),
        "api_football_key_loaded": bool(os.getenv("API_FOOTBALL_KEY")),
    }


@app.get("/api/score")
async def score(
    probability: float = Query(..., ge=0, le=100),
    forebet: float = Query(0, ge=0, le=100),
    tipsters: float = Query(0, ge=0, le=100),
    stats: float = Query(0, ge=0, le=100),
    odds: float = Query(..., gt=1),
) -> dict[str, float]:
    return calc_ai_score(probability, forebet, tipsters, stats, odds)


@app.get("/api/footystats/todays-matches")
async def footystats_today() -> JSONResponse:
    key = os.getenv("FOOTYSTATS_API_KEY")
    if not key:
        return JSONResponse(
            status_code=400,
            content={"error": "FOOTYSTATS_API_KEY is missing"},
        )

    url = "https://api.footystats.org/todays-matches"
    params = {"key": key}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params=params)
            try:
                data = response.json()
            except Exception:
                data = {"raw": response.text}
            return JSONResponse(content=data, status_code=response.status_code)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"error": "FootyStats request failed", "details": str(exc)},
        )
