"""Local-only OCR API for Susegad Desk. Run with: uvicorn server:app --host 0.0.0.0 --port 8000"""
from __future__ import annotations

import io
import json
import os
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps
import pytesseract
import requests

app = FastAPI(title="Susegad Desk", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
MAX_IMAGE_BYTES = 10 * 1024 * 1024


@app.get("/")
def home() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/api/health")
def health() -> dict[str, Any]:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        models = [m.get("name", "") for m in r.json().get("models", [])] if r.ok else []
    except requests.RequestException:
        models = []
    return {"ok": True, "ollama": OLLAMA_MODEL in models or any(x.startswith(OLLAMA_MODEL.split(":")[0] + ":") for x in models), "model": OLLAMA_MODEL}


@app.post("/api/extract")
async def extract(file: UploadFile = File(...)) -> dict[str, Any]:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(415, "Upload a JPG, PNG, or WebP image.")
    raw = await file.read(MAX_IMAGE_BYTES + 1)
    if not raw or len(raw) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Image must be between 1 byte and 10 MB.")
    try:
        image = Image.open(io.BytesIO(raw))
        image.verify()
        image = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    except Exception as exc:
        raise HTTPException(400, "Could not read that image.") from exc
    # OCR runs locally. The image and OCR text are only held in memory for this request.
    text = pytesseract.image_to_string(image, lang=os.getenv("TESSERACT_LANG", "eng"))[:12000]
    if not text.strip():
        raise HTTPException(422, "No readable text found. Try a sharper, well-lit image.")
    prompt = f'''Extract only fields that are clearly present in this OCR text. Do not guess. Return one JSON object with string values for full_name, age, address, id_type, id_number. Use empty strings for unknown values. Preserve original spelling and do not infer age from dates. OCR text:\n{text}'''
    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json", "options": {"temperature": 0}}, timeout=90)
        response.raise_for_status()
        content = response.json().get("response", "")
        fields = json.loads(content)
        if not isinstance(fields, dict):
            raise ValueError("Expected JSON object")
    except (requests.RequestException, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(503, "Local extraction model unavailable or returned invalid JSON. Check Ollama and try again.") from exc
    allowed = ("full_name", "age", "address", "id_type", "id_number")
    cleaned = {k: str(fields.get(k, ""))[:500] for k in allowed}
    return {"fields": cleaned, "review_required": True, "ocr_text": text}
