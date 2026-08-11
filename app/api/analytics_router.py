import io
import csv
from datetime import datetime, date
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Response

from app.api.ws_router import get_analytics_engine, get_energy_logger

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def parse_date_arg(date_str: Optional[str]) -> date:
    if not date_str or date_str.lower() in ("today", "now"):
        return datetime.now().date()
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format '{date_str}'. Expected YYYY-MM-DD.",
        )


@router.get("/hourly")
@router.get("/hourly/{date_str}")
def get_hourly_analytics(date_str: Optional[str] = None):
    """
    Returns 24-hour breakdown (00:00 - 23:59) for specified date.
    Date format: YYYY-MM-DD (defaults to today if omitted).
    """
    target_date = parse_date_arg(date_str)
    engine = get_analytics_engine()
    hourly_summary = engine.get_hourly_summary(target_date=target_date)
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "hourly_summary": hourly_summary,
    }


@router.get("/daily")
@router.get("/daily/{date_str}")
def get_daily_summary(date_str: Optional[str] = None):
    """
    Returns consolidated daily energy metrics and device usage breakdown.
    """
    target_date = parse_date_arg(date_str)
    engine = get_analytics_engine()
    daily_summary = engine.get_daily_summary(target_date=target_date)
    return daily_summary


@router.get("/weekly")
def get_weekly_trend():
    """
    Returns 7-day rolling trend summary metrics for sparkline visualization.
    """
    engine = get_analytics_engine()
    weekly_summary = engine.get_weekly_summary()
    return {
        "weekly_trend": weekly_summary,
    }


@router.get("/export/csv")
def export_csv_report(date_str: Optional[str] = Query(None, alias="date")):
    """
    Exports 24-hour hourly aggregated summary as a downloadable CSV report.
    """
    target_date = parse_date_arg(date_str)
    engine = get_analytics_engine()
    hourly_data = engine.get_hourly_summary(target_date=target_date)

    output = io.StringIO()
    fieldnames = [
        "hour",
        "kwh_actual",
        "kwh_baseline",
        "kwh_saved",
        "avg_power_watts",
        "peak_power_watts",
        "schedule_active",
        "active_hours",
        "occupancy_events",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in hourly_data:
        writer.writerow(row)

    csv_content = output.getvalue()
    filename = f"energy_analytics_summary_{target_date.strftime('%Y-%m-%d')}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
