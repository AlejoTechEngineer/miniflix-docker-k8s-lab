"""recommendation-service: personaliza el catálogo por perfil.

Patrones demostrados:
  * descubrimiento por DNS del orquestador (CATALOG_URL=http://catalog:8000)
  * caché distribuida opcional (Redis) con TTL
  * degradación elegante: si catalog no responde, se sirve un fallback
"""
import json
import os

import httpx
from fastapi import FastAPI

app = FastAPI(title="recommendation-service", version="1.0.0")
INSTANCE = os.getenv("HOSTNAME", "local")
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:8000")
REDIS_URL = os.getenv("REDIS_URL")
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "60"))
TIMEOUT = float(os.getenv("CATALOG_TIMEOUT_SECONDS", "0.8"))

# Afinidad de género simulada por perfil (en producción: un modelo de ML)
PROFILE_AFFINITY = {
    "p-ana": {"drama": 0.9, "documental": 0.6},
    "p-luis": {"thriller": 0.9, "ciencia-ficcion": 0.8},
}
FALLBACK = [{"id": "t4", "name": "Bogotá 2049", "reason": "fallback-popular"}]

_cache = None
if REDIS_URL:
    try:
        import redis

        _cache = redis.Redis.from_url(REDIS_URL, socket_timeout=0.3)
    except Exception:  # la caché nunca debe tumbar el servicio
        _cache = None


def _cache_get(key):
    if not _cache:
        return None
    try:
        raw = _cache.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def _cache_set(key, value):
    if not _cache:
        return
    try:
        _cache.setex(key, CACHE_TTL, json.dumps(value))
    except Exception:
        pass


@app.get("/health")
def health():
    return {"status": "UP", "service": "recommendation", "instance": INSTANCE,
            "cache": "redis" if _cache else "disabled"}


@app.get("/recommendations/{profile_id}")
def recommend(profile_id: str, limit: int = 3):
    key = f"recs:{profile_id}:{limit}"
    cached = _cache_get(key)
    if cached:
        return {**cached, "source": "cache", "served_by": INSTANCE}

    try:
        resp = httpx.get(f"{CATALOG_URL}/titles", timeout=TIMEOUT)
        resp.raise_for_status()
        titles = resp.json()["items"]
    except Exception:
        # Degradación elegante: el usuario sigue viendo algo útil
        return {"profile": profile_id, "items": FALLBACK, "source": "fallback",
                "served_by": INSTANCE}

    affinity = PROFILE_AFFINITY.get(profile_id, {})
    scored = sorted(
        titles,
        key=lambda t: affinity.get(t["genre"], 0.3) * 100 + t["popularity"] * 0.5,
        reverse=True,
    )
    result = {"profile": profile_id,
              "items": [{"id": t["id"], "name": t["name"], "genre": t["genre"]}
                        for t in scored[:limit]]}
    _cache_set(key, result)
    return {**result, "source": "computed", "served_by": INSTANCE}
