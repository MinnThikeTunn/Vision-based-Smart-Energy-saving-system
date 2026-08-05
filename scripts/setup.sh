#!/usr/bin/env bash
set -e

echo "=================================================="
echo " Vision-Based Smart Energy Saving System Bootstrap "
echo "=================================================="

if [ ! -d ".venv" ]; then
    echo "[1/3] Creating virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "[1/3] Virtual environment (.venv) already exists."
fi

echo "[2/3] Installing dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt websockets

echo "[3/3] Starting FastAPI server on http://127.0.0.1:8000 ..."
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
