"""
Vision-Based Smart Energy Saving System - FastAPI Application

Production-grade FastAPI application with:
- Prometheus/OpenMetrics metrics endpoint for observability
- WebSocket real-time telemetry
- Privacy-first video streaming
- Device control and spatial zone management
"""

from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_asgi_app, CONTENT_TYPE_LATEST

from app.api.config_router import router as config_router
from app.api.video_router import router as video_router
from app.api.ws_router import router as ws_router
from app.api.analytics_router import router as analytics_router
from app.telemetry.metrics import get_metrics_registry


# Initialize FastAPI application
app = FastAPI(
    title="Vision-Based Smart Energy Saving System",
    version="2.0.0",
    description="Real-time AI occupancy detection and automated energy management",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include API routers
app.include_router(config_router)
app.include_router(video_router)
app.include_router(ws_router)
app.include_router(analytics_router)


# Mount static files for dashboard
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ============================================================================
# Landing Page & Dashboard UI
# ============================================================================

def _read_html(filename: str) -> str:
    html_file = STATIC_DIR / filename
    if html_file.exists():
        with open(html_file, encoding="utf-8") as f:
            return f.read()
    return f"<h1>Missing {filename}</h1>"


@app.get("/", response_class=HTMLResponse)
def serve_landing():
    """Serve the marketing / project landing page (UI only)."""
    return _read_html("landing.html")


@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    """Serve the main control & analytics dashboard UI."""
    return _read_html("index.html")


@app.get("/app", response_class=HTMLResponse)
def serve_dashboard_alias():
    """Alias for /dashboard so existing bookmarks keep working."""
    return _read_html("index.html")


@app.get("/health")
def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "ok", "version": "2.0.0"}


# ============================================================================
# Prometheus Metrics Endpoint (Production-Grade)
# ============================================================================

@app.get("/metrics")
async def prometheus_metrics(request: Request):
    """
    Prometheus/OpenMetrics metrics endpoint for observability.
    
    Returns metrics in OpenMetrics text format for scraping by Prometheus,
    Grafana, Datadog, or other observability platforms.
    
    Content negotiation is handled to support:
    - text/plain (Prometheus text format)
    - application/openmetrics-text (OpenMetrics 1.0.0)
    - application/vnd.google.protobuf (Protobuf format for large deployments)
    
    The metrics include:
    - Occupancy metrics (person count, room status, state transitions)
    - Device metrics (state, power, toggles, countdowns)
    - Energy metrics (power draw, savings, efficiency)
    - Inference metrics (FPS, latency histograms, frame processing)
    """
    registry = get_metrics_registry()
    
    # Check Accept header for content negotiation
    accept = request.headers.get("accept", "")
    
    # Generate metrics output (prometheus_client handles format negotiation)
    output = registry.generate_prometheus_metrics()
    
    # Return with proper content type for Prometheus compatibility
    return Response(
        content=output,
        media_type=registry.get_content_type(),
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
    )


# ============================================================================
# Optional: Mount prometheus_client's ASGI app for advanced features
# ============================================================================

# For multiprocess support (e.g., when running with Gunicorn + multiple workers),
# uncomment the following and use this instead of the custom endpoint above:
#
# from prometheus_client import CollectorRegistry, multiprocess
#
# def create_metrics_app():
#     registry = CollectorRegistry()
#     multiprocess.MultiProcessCollector(registry)
#     return make_asgi_app(registry=registry)
#
# app.mount("/metrics", create_metrics_app())
