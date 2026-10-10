"""catalog-service: fuente de verdad del catálogo (metadatos de títulos)."""
import os

from fastapi import FastAPI, HTTPException

app = FastAPI(title="catalog-service", version="1.0.0")
INSTANCE = os.getenv("HOSTNAME", "local")

TITLES = [
    {"id": "t1", "name": "Frontera Andina", "genre": "drama", "year": 2024, "popularity": 91},
    {"id": "t2", "name": "Código Caribe", "genre": "thriller", "year": 2025, "popularity": 88},
    {"id": "t3", "name": "La Ruta del Café", "genre": "documental", "year": 2023, "popularity": 74},
    {"id": "t4", "name": "Bogotá 2049", "genre": "ciencia-ficcion", "year": 2026, "popularity": 95},
    {"id": "t5", "name": "Selva Interior", "genre": "drama", "year": 2022, "popularity": 69},
    {"id": "t6", "name": "Protocolo Cero", "genre": "thriller", "year": 2026, "popularity": 83},
    {"id": "t7", "name": "Órbita Baja", "genre": "ciencia-ficcion", "year": 2025, "popularity": 77},
]
INDEX = {t["id"]: t for t in TITLES}


@app.get("/health")
def health():
    return {"status": "UP", "service": "catalog", "instance": INSTANCE}


@app.get("/titles")
def list_titles(genre: str | None = None):
    items = [t for t in TITLES if genre is None or t["genre"] == genre]
    return {"count": len(items), "items": items, "served_by": INSTANCE}


@app.get("/titles/{title_id}")
def get_title(title_id: str):
    if title_id not in INDEX:
        raise HTTPException(status_code=404, detail="title not found")
    return INDEX[title_id]
