"""
Main FastAPI Application Entrypoint for IDX Emiten KeyStats & Scoring Engine.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.emiten import router as emiten_router
from app.api.v1.compare import router as compare_router
from app.api.v1.screener import router as screener_router
from app.api.v1.market import router as market_router
from app.api.v1.currency import router as currency_router
from app.api.v1.chart import router as chart_router
from app.api.v1.calendar import router as calendar_router

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="IDX Emiten KeyStats & Scoring Engine API",
    description="Institutional-grade Fundamental Analysis, Multi-Model Valuation, and Scoring API for Indonesian Stock Exchange (IDX) emitens.",
    version="1.0.0"
)

# Enable CORS for Next.js / Web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routers
app.include_router(market_router, prefix="/api/v1")
app.include_router(currency_router, prefix="/api/v1")
app.include_router(calendar_router, prefix="/api/v1")
app.include_router(emiten_router, prefix="/api/v1")
app.include_router(compare_router, prefix="/api/v1")
app.include_router(screener_router, prefix="/api/v1")
app.include_router(chart_router, prefix="/api/v1")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "idx-keystats-engine", "version": "1.0.0"}


@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Welcome to IDX Emiten KeyStats & Scoring Engine API",
        "docs": "/docs"
    }
