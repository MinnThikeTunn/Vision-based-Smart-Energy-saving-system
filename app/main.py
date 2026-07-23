from fastapi import FastAPI
from app.api.config_router import router as config_router

app = FastAPI(
    title="Vision-Based Smart Energy Saving System",
    version="0.1.0",
)

app.include_router(config_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
