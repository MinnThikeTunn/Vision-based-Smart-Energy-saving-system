from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from app.api.config_router import router as config_router
from app.api.video_router import router as video_router
from app.api.ws_router import router as ws_router
from app.telemetry.metrics import get_metrics_registry

app = FastAPI(
    title="Vision-Based Smart Energy Saving System",
    version="2.0.0",
)

app.include_router(config_router)
app.include_router(video_router)
app.include_router(ws_router)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        with open(index_file, encoding="utf-8") as f:
            return f.read()
    return "<h1>Vision Smart Energy Saver API Running</h1>"


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/metrics", response_class=PlainTextResponse)
def prometheus_metrics():
    registry = get_metrics_registry()
    return registry.generate_prometheus_metrics()
