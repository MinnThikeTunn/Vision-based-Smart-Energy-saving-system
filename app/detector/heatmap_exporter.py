import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional


ZONE_PALETTE = [
    (255, 200, 0),    # Bright Cyan
    (255, 0, 220),    # Vivid Magenta
    (80, 255, 120),   # Emerald Neon
    (0, 215, 255),    # Vibrant Amber / Gold
    (0, 140, 255),    # Safety Orange
    (255, 120, 180),  # Soft Purple / Lavender
    (0, 255, 200),    # Mint Green
    (180, 255, 0),    # Electric Lime
]


def create_dwell_colorbar(width: int = 160, height: int = 12) -> np.ndarray:
    """Create a horizontal JET colormap gradient strip."""
    gradient = np.linspace(0, 255, width, dtype=np.uint8)
    gradient_2d = np.tile(gradient, (height, 1))
    colorbar = cv2.applyColorMap(gradient_2d, cv2.COLORMAP_JET)
    # Add subtle 1px border
    cv2.rectangle(colorbar, (0, 0), (width - 1, height - 1), (80, 80, 90), 1)
    return colorbar


def render_zone_overlays(
    canvas: np.ndarray,
    spatial_zones: Optional[List[Any]] = None,
    zone_stats: Optional[Dict[str, float]] = None,
) -> np.ndarray:
    """
    Renders styled spatial zone boundaries, corner brackets, and information badges
    directly onto the heatmap canvas.
    """
    if not spatial_zones:
        return canvas

    annotated = canvas.copy()
    h, w = annotated.shape[:2]
    stats = zone_stats or {}

    for idx, zone in enumerate(spatial_zones):
        name = getattr(zone, "name", None) or (zone.get("name") if isinstance(zone, dict) else f"Zone {idx+1}")
        assigned = getattr(zone, "assigned_devices", None) or (zone.get("assigned_devices") if isinstance(zone, dict) else [])
        b = getattr(zone, "bbox", None) or (zone.get("bbox") if isinstance(zone, dict) else [0.0, 0.0, 1.0, 1.0])
        color = ZONE_PALETTE[idx % len(ZONE_PALETTE)]
        util_pct = stats.get(name, 0.0)

        # Compute bounding box pixel coordinates
        if len(b) >= 4:
            if max(b) <= 1.0:
                x1, y1 = int(b[0] * w), int(b[1] * h)
                x2, y2 = int(b[2] * w), int(b[3] * h)
            else:
                x1, y1, x2, y2 = int(b[0]), int(b[1]), int(b[2]), int(b[3])
        else:
            x1, y1, x2, y2 = 0, 0, w, h

        x1, y1 = max(0, min(w - 1, x1)), max(0, min(h - 1, y1))
        x2, y2 = max(0, min(w - 1, x2)), max(0, min(h - 1, y2))

        if x2 <= x1 or y2 <= y1:
            continue

        # 1. Subtle semi-transparent zone fill (12% opacity)
        zone_mask = annotated.copy()
        cv2.rectangle(zone_mask, (x1, y1), (x2, y2), color, -1)
        annotated = cv2.addWeighted(annotated, 0.88, zone_mask, 0.12, 0)

        # 2. Zone outline
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)

        # 3. Corner tick bracket accents
        cw = min(16, max(6, (x2 - x1) // 5))
        ch = min(16, max(6, (y2 - y1) // 5))
        # Top-Left
        cv2.line(annotated, (x1, y1), (x1 + cw, y1), color, 3)
        cv2.line(annotated, (x1, y1), (x1, y1 + ch), color, 3)
        # Top-Right
        cv2.line(annotated, (x2, y1), (x2 - cw, y1), color, 3)
        cv2.line(annotated, (x2, y1), (x2, y1 + ch), color, 3)
        # Bottom-Left
        cv2.line(annotated, (x1, y2), (x1 + cw, y2), color, 3)
        cv2.line(annotated, (x1, y2), (x1, y2 - ch), color, 3)
        # Bottom-Right
        cv2.line(annotated, (x2, y2), (x2 - cw, y2), color, 3)
        cv2.line(annotated, (x2, y2), (x2, y2 - ch), color, 3)

        # 4. In-Zone Info Badge
        dev_str = ", ".join(assigned) if assigned else "None"
        line1 = f"{name}"
        line2 = f"Dev: {dev_str}  |  Heat: {util_pct:.1f}%"

        font = cv2.FONT_HERSHEY_SIMPLEX
        scale1, scale2 = 0.44, 0.36
        (t1_w, t1_h), _ = cv2.getTextSize(line1, font, scale1, 1)
        (t2_w, t2_h), _ = cv2.getTextSize(line2, font, scale2, 1)

        badge_w = max(t1_w + 26, t2_w + 16) + 14
        badge_h = t1_h + t2_h + 20

        bx = min(max(x1 + 8, 8), max(8, w - badge_w - 8))
        by = min(max(y1 + 8, 8), max(8, h - badge_h - 8))

        # Badge background with rounded feel
        cv2.rectangle(
            annotated,
            (bx, by),
            (bx + badge_w, by + badge_h),
            (12, 12, 16),
            -1,
        )
        cv2.rectangle(
            annotated,
            (bx, by),
            (bx + badge_w, by + badge_h),
            (55, 55, 68),
            1,
            cv2.LINE_AA,
        )

        # Color dot next to title
        cv2.circle(annotated, (bx + 10, by + t1_h + 3), 4, color, -1)

        # Text Line 1: Zone Name
        cv2.putText(
            annotated,
            line1,
            (bx + 20, by + t1_h + 6),
            font,
            scale1,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        # Text Line 2: Assigned Devices & Heat Utilization
        cv2.putText(
            annotated,
            line2,
            (bx + 10, by + t1_h + t2_h + 14),
            font,
            scale2,
            (180, 220, 205),
            1,
            cv2.LINE_AA,
        )

    return annotated


def render_heatmap_export_image(
    acc_map: Optional[np.ndarray],
    spatial_zones: Optional[List[Any]] = None,
    window: str = "5m",
    max_saturation_sec: float = 300.0,
    bg_frame: Optional[np.ndarray] = None,
    headless_mode: bool = False,
    zone_stats: Optional[Dict[str, float]] = None,
    timestamp_str: Optional[str] = None,
) -> np.ndarray:
    """
    Renders an audit-grade PNG heatmap snapshot complete with:
    1. High-contrast header bar (Title, time window, dwell saturation cap, room coverage %, timestamp).
    2. Main spatial occupancy heatmap blended with grid/frame and zone boundaries & info badges.
    3. Bottom telemetry footer with Dwell density colorbar and detailed zone inventory cards.
    """
    if timestamp_str is None:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    h, w = (480, 640)
    if acc_map is not None and acc_map.size > 0:
        h, w = acc_map.shape[:2]
    elif bg_frame is not None and bg_frame.size > 0:
        h, w = bg_frame.shape[:2]

    # Target minimum width for crisp readability
    canvas_w = max(w, 720)
    canvas_h = h

    # -------------------------------------------------------------
    # 1. GENERATE BASE HEATMAP VISUAL
    # -------------------------------------------------------------
    if acc_map is not None and acc_map.size > 0:
        norm = np.clip((acc_map / max(1e-5, max_saturation_sec)) * 255.0, 0, 255).astype(np.uint8)
    else:
        norm = np.zeros((h, w), dtype=np.uint8)

    heatmap_overlay = cv2.applyColorMap(norm, cv2.COLORMAP_JET)

    # Base grid / background
    if headless_mode or bg_frame is None:
        base_grid = np.full((h, w, 3), 16, dtype=np.uint8)
        # Spatial reference grid lines
        for y in range(0, h, 40):
            cv2.line(base_grid, (0, y), (w, y), (30, 34, 40), 1)
        for x in range(0, w, 40):
            cv2.line(base_grid, (x, 0), (x, h), (30, 34, 40), 1)
        main_visual = cv2.addWeighted(base_grid, 0.40, heatmap_overlay, 0.60, 0)
    else:
        frame_resized = cv2.resize(bg_frame, (w, h)) if bg_frame.shape[:2] != (h, w) else bg_frame.copy()
        main_visual = cv2.addWeighted(frame_resized, 0.45, heatmap_overlay, 0.55, 0)

    # Resize main visual if canvas width is expanded
    if canvas_w != w:
        main_visual = cv2.resize(main_visual, (canvas_w, canvas_h), interpolation=cv2.INTER_AREA)

    # -------------------------------------------------------------
    # 2. OVERLAY SPATIAL ZONES ON MAIN VISUAL
    # -------------------------------------------------------------
    main_visual = render_zone_overlays(
        main_visual,
        spatial_zones=spatial_zones,
        zone_stats=zone_stats,
    )

    # -------------------------------------------------------------
    # 3. BUILD HEADER BAR (Height: 64px)
    # -------------------------------------------------------------
    header_h = 64
    header = np.full((header_h, canvas_w, 3), 14, dtype=np.uint8)
    # Bottom separator line
    cv2.line(header, (0, header_h - 1), (canvas_w, header_h - 1), (45, 45, 54), 1)

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Left: Title & Subtitle
    cv2.putText(
        header,
        "SPATIAL OCCUPANCY HEATMAP AUDIT",
        (16, 26),
        font,
        0.54,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    overall_cov = zone_stats.get("overall", 0.0) if zone_stats else 0.0
    subtitle_text = f"Window: {window.upper()}  |  Cap: {int(max_saturation_sec)}s  |  Resolution: {canvas_w}x{canvas_h}px"
    cv2.putText(
        header,
        subtitle_text,
        (16, 48),
        font,
        0.36,
        (150, 160, 175),
        1,
        cv2.LINE_AA,
    )

    # Right: Timestamp & Room Coverage
    ts_text = f"Exported: {timestamp_str}"
    (ts_w, _), _ = cv2.getTextSize(ts_text, font, 0.36, 1)
    cv2.putText(
        header,
        ts_text,
        (canvas_w - ts_w - 16, 25),
        font,
        0.36,
        (180, 220, 200),
        1,
        cv2.LINE_AA,
    )

    cov_text = f"Room Heat Coverage: {overall_cov:.1f}%"
    (cov_w, _), _ = cv2.getTextSize(cov_text, font, 0.42, 1)
    cv2.putText(
        header,
        cov_text,
        (canvas_w - cov_w - 16, 48),
        font,
        0.42,
        (0, 215, 255),
        1,
        cv2.LINE_AA,
    )

    # -------------------------------------------------------------
    # 4. BUILD FOOTER BAR (Legend + Zone Summary Cards)
    # -------------------------------------------------------------
    zones_list = spatial_zones or []
    cards_per_row = 2 if canvas_w >= 640 else 1
    zone_rows = (len(zones_list) + cards_per_row - 1) // cards_per_row if zones_list else 1
    footer_h = 48 + max(1, zone_rows) * 34 + 10

    footer = np.full((footer_h, canvas_w, 3), 18, dtype=np.uint8)
    # Top separator line
    cv2.line(footer, (0, 0), (canvas_w, 0), (45, 45, 54), 1)

    # Dwell Colorbar Legend Row
    cv2.putText(
        footer,
        "Dwell Density Scale:",
        (16, 25),
        font,
        0.38,
        (160, 165, 175),
        1,
        cv2.LINE_AA,
    )

    cv2.putText(
        footer,
        "0% (Low Dwell)",
        (162, 25),
        font,
        0.34,
        (220, 180, 130),
        1,
        cv2.LINE_AA,
    )

    cbar = create_dwell_colorbar(width=140, height=10)
    cbar_x = 265
    cbar_y = 16
    footer[cbar_y : cbar_y + 10, cbar_x : cbar_x + 140] = cbar

    cv2.putText(
        footer,
        "100% (High Dwell)",
        (cbar_x + 150, 25),
        font,
        0.34,
        (120, 120, 255),
        1,
        cv2.LINE_AA,
    )

    # Right side of legend row: Zone Count indicator
    zone_cnt_text = f"Spatial Zones: {len(zones_list)}"
    (zcnt_w, _), _ = cv2.getTextSize(zone_cnt_text, font, 0.36, 1)
    cv2.putText(
        footer,
        zone_cnt_text,
        (canvas_w - zcnt_w - 16, 25),
        font,
        0.36,
        (180, 185, 195),
        1,
        cv2.LINE_AA,
    )

    # Zone Information Cards
    if not zones_list:
        cv2.putText(
            footer,
            "No custom spatial zones configured (Global full-room monitoring active)",
            (16, 56),
            font,
            0.36,
            (140, 145, 155),
            1,
            cv2.LINE_AA,
        )
    else:
        card_w = (canvas_w - 32 - (cards_per_row - 1) * 12) // cards_per_row
        card_h = 28

        for idx, zone in enumerate(zones_list):
            row_idx = idx // cards_per_row
            col_idx = idx % cards_per_row

            card_x = 16 + col_idx * (card_w + 12)
            card_y = 42 + row_idx * 32

            z_name = getattr(zone, "name", None) or (zone.get("name") if isinstance(zone, dict) else f"Zone {idx+1}")
            z_devices = getattr(zone, "assigned_devices", None) or (zone.get("assigned_devices") if isinstance(zone, dict) else [])
            z_color = ZONE_PALETTE[idx % len(ZONE_PALETTE)]
            z_pct = zone_stats.get(z_name, 0.0) if zone_stats else 0.0
            devs_text = ", ".join(z_devices) if z_devices else "None"

            # Draw card background pill
            cv2.rectangle(
                footer,
                (card_x, card_y),
                (card_x + card_w, card_y + card_h),
                (26, 26, 32),
                -1,
            )
            cv2.rectangle(
                footer,
                (card_x, card_y),
                (card_x + card_w, card_y + card_h),
                (50, 50, 60),
                1,
                cv2.LINE_AA,
            )

            # Color swatch
            cv2.rectangle(
                footer,
                (card_x + 6, card_y + 6),
                (card_x + 18, card_y + 22),
                z_color,
                -1,
            )

            # Text content
            card_text = f"{z_name}  |  Devices: {devs_text}  |  Heat: {z_pct:.1f}%"
            cv2.putText(
                footer,
                card_text,
                (card_x + 24, card_y + 19),
                font,
                0.34,
                (230, 230, 235),
                1,
                cv2.LINE_AA,
            )

    # -------------------------------------------------------------
    # 5. ASSEMBLE COMPLETE CANVAS
    # -------------------------------------------------------------
    full_image = np.vstack([header, main_visual, footer])
    return full_image
