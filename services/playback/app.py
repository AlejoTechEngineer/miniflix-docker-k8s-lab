"""playback-service: autoriza la reproducción y devuelve el manifiesto + URL de CDN.

Simula el 'steering' del plano de control: este servicio no transmite video,
solo indica al cliente desde qué nodo de borde (CDN) descargar los segmentos.
"""
import os
import uuid

import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI(title="playback-service", version="1.0.0")
INSTANCE = os.getenv("HOSTNAME", "local")
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:8000")
CDN_BASE_URL = os.getenv("CDN_BASE_URL", "http://localhost:8080/cdn")


@app.get("/health")
def health():
    return {"status": "UP", "service": "playback", "instance": INSTANCE}


@app.post("/playback/{title_id}")
def start_playback(title_id: str, profile: str = "anonymous"):
    try:
        r = httpx.get(f"{CATALOG_URL}/titles/{title_id}", timeout=0.8)
    except Exception:
        raise HTTPException(status_code=503, detail="catalog unavailable")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="title not found")
    title = r.json()
    return {
        "session_id": str(uuid.uuid4()),
        "title": title["name"],
        "profile": profile,
        "manifest_url": f"{CDN_BASE_URL}/{title_id}/manifest.json",
        "bitrate_ladder_kbps": [235, 750, 1750, 3000, 5800],
        "served_by": INSTANCE,
    }
