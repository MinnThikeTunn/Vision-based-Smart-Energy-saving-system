from typing import Optional
import cv2
from fastapi import APIRouter
from fastapi.responses import Response, StreamingResponse
import numpy as np

from app.detector.pipeline import VisionPipeline

router = APIRouter(prefix="/api", tags=["video"])

_pipeline_instance: Optional[VisionPipeline] = None


def get_vision_pipeline() -> VisionPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        from app.config.loader import load_settings
        from app.detector.person_detector import DummyDetector, YOLOPersonDetector

        settings = load_settings()
        detector_cfg = settings.detector
        camera_cfg = settings.camera

        try:
            detector = YOLOPersonDetector(
                model_name=detector_cfg.model_name,
                confidence_threshold=detector_cfg.confidence_threshold,
                device=detector_cfg.device,
            )
            print(f"Successfully loaded YOLOPersonDetector using model {detector_cfg.model_name}")
        except Exception as e:
            print(f"[WARNING] Failed to load YOLO detector ({e}). Falling back to DummyDetector.")
            print("[HINT] Ensure uvicorn is started using the project virtual environment: .venv\\Scripts\\uvicorn.exe app.main:app --reload")
            detector = DummyDetector()

        _pipeline_instance = VisionPipeline(
            detector=detector,
            camera_index=camera_cfg.index,
            fps_target=camera_cfg.fps,
            anonymize_faces=settings.privacy.anonymize_faces,
        )
        _pipeline_instance.start()
    else:
        from app.config.loader import load_settings
        from app.detector.person_detector import YOLOPersonDetector
        try:
            settings = load_settings()
            if isinstance(_pipeline_instance.detector, YOLOPersonDetector):
                _pipeline_instance.detector.confidence_threshold = settings.detector.confidence_threshold
                _pipeline_instance.detector.device = settings.detector.device
            _pipeline_instance.anonymize_faces = settings.privacy.anonymize_faces
        except Exception:
            pass

    return _pipeline_instance


def set_vision_pipeline(pipeline: VisionPipeline) -> None:
    global _pipeline_instance
    _pipeline_instance = pipeline


@router.get("/video_feed")
def video_feed(heatmap: bool = False, window: str = "instant", alpha: float = 0.3):
    from app.config.loader import load_settings
    settings = load_settings()
    pipeline = get_vision_pipeline()

    # Headless Automation Mode: privacy interaction
    if settings.privacy.headless_mode:
        if heatmap:
            # Render Headless Dark Grid Heatmap Overlay
            acc_map = pipeline._get_accumulator_matrix(window)
            grid = np.zeros((480, 640, 3), dtype=np.uint8)
            # Add subtle grid lines for spatial reference
            for y in range(0, 480, 40):
                cv2.line(grid, (0, y), (640, y), (30, 35, 40), 1)
            for x in range(0, 640, 40):
                cv2.line(grid, (x, 0), (x, 480), (30, 35, 40), 1)

            cv2.putText(grid, "HEADLESS HEATMAP AUDIT GRID", (150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 200), 2)

            if acc_map is not None and acc_map.size > 0:
                norm = np.clip((acc_map / pipeline.max_saturation_sec) * 255.0, 0, 255).astype(np.uint8)
                heatmap_overlay = cv2.applyColorMap(norm, cv2.COLORMAP_JET)
                grid = cv2.addWeighted(grid, 0.5, heatmap_overlay, 0.5, 0)

            _, jpeg = cv2.imencode(".jpg", grid)
            return Response(content=jpeg.tobytes(), media_type="image/jpeg")
        else:
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                placeholder,
                "Headless Mode Active",
                (170, 220),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 200),
                2,
            )
            cv2.putText(
                placeholder,
                "(Video Stream Disabled for Privacy)",
                (120, 260),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (200, 200, 200),
                1,
            )
            _, jpeg = cv2.imencode(".jpg", placeholder)
            return Response(content=jpeg.tobytes(), media_type="image/jpeg")

    return StreamingResponse(
        pipeline.generate_mjpeg_stream(draw_heatmap=heatmap, window=window, alpha=alpha),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.post("/heatmap/reset")
def reset_heatmap(window: str = "all"):
    pipeline = get_vision_pipeline()
    pipeline.reset_heatmap_accumulator(window=window)
    return {"status": "ok", "message": f"Heatmap accumulator buffer ({window}) reset successfully."}


@router.get("/heatmap/stats")
def heatmap_stats(window: str = "5m"):
    from app.config.loader import load_settings
    settings = load_settings()
    pipeline = get_vision_pipeline()
    stats = pipeline.get_zone_heatmap_stats(spatial_zones=settings.spatial_zones, window=window)
    return {"window": window, "spatial_utilization": stats}


@router.get("/heatmap/export")
def export_heatmap(window: str = "5m", include_zones: bool = True):
    from pathlib import Path
    from datetime import datetime
    from app.config.loader import load_settings
    from app.detector.heatmap_exporter import render_heatmap_export_image

    settings = load_settings()
    pipeline = get_vision_pipeline()
    acc_map = pipeline._get_accumulator_matrix(window)
    zones = settings.spatial_zones if include_zones else []
    stats = pipeline.get_zone_heatmap_stats(spatial_zones=zones, window=window)
    bg_frame, _, _ = pipeline.get_latest_processed(draw_heatmap=False)

    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_file = now.strftime("%Y%m%d_%H%M%S")

    exported_image = render_heatmap_export_image(
        acc_map=acc_map,
        spatial_zones=zones,
        window=window,
        max_saturation_sec=pipeline.max_saturation_sec,
        bg_frame=bg_frame,
        headless_mode=settings.privacy.headless_mode,
        zone_stats=stats,
        timestamp_str=timestamp_str,
    )

    # Save snapshot to storage/heatmaps/
    storage_dir = Path("storage/heatmaps")
    storage_dir.mkdir(parents=True, exist_ok=True)
    filename = f"heatmap_{timestamp_file}_{window}.png"
    filepath = storage_dir / filename
    cv2.imwrite(str(filepath), exported_image)

    ret, png_bytes = cv2.imencode(".png", exported_image)
    if not ret:
        return Response(content=b"", media_type="image/png")

    return Response(
        content=png_bytes.tobytes(),
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

