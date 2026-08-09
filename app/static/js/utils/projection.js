/**
 * Video Aspect-Ratio & Object-Contain Letterbox Coordinate Projection Utility
 */
export function getNormalizedVideoCoordinates(event, canvasEl, videoEl) {
  const rect = canvasEl.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const clickY = event.clientY - rect.top;

  const containerW = canvasEl.width;
  const containerH = canvasEl.height;

  // Intrinsic video frame dimensions (default to 640x480 if not loaded)
  const videoW = (videoEl && videoEl.videoWidth) ? videoEl.videoWidth : 640;
  const videoH = (videoEl && videoEl.videoHeight) ? videoEl.videoHeight : 480;

  const containerAspect = containerW / containerH;
  const videoAspect = videoW / videoH;

  let renderW, renderH, offsetX, offsetY;

  if (containerAspect > videoAspect) {
    // Pillarboxed (black bars on left & right)
    renderH = containerH;
    renderW = containerH * videoAspect;
    offsetX = (containerW - renderW) / 2;
    offsetY = 0;
  } else {
    // Letterboxed (black bars on top & bottom)
    renderW = containerW;
    renderH = containerW / videoAspect;
    offsetX = 0;
    offsetY = (containerH - renderH) / 2;
  }

  // Normalize relative to actual video frame pixels
  const normX = Math.max(0, Math.min(1, (clickX - offsetX) / renderW));
  const normY = Math.max(0, Math.min(1, (clickY - offsetY) / renderH));

  return {
    normX: parseFloat(normX.toFixed(4)),
    normY: parseFloat(normY.toFixed(4)),
  };
}
