#!/usr/bin/env bash
# Prueba de humo end-to-end contra el gateway (docker compose up -d --build primero)
set -euo pipefail
BASE="${BASE:-http://localhost:8080}"
pass() { echo "  [OK] $1"; }
echo "Mini-Flix smoke test contra $BASE"
curl -fsS "$BASE/health" >/dev/null                                    && pass "gateway"
curl -fsS "$BASE/api/catalog/titles" | grep -q '"count":7'              && pass "catálogo"
curl -fsS "$BASE/api/recs/p-luis"    | grep -q '"items"'                && pass "recomendaciones"
curl -fsS -X POST "$BASE/api/play/t1?profile=p-ana" | grep -q manifest  && pass "reproducción"
curl -fsS "$BASE/cdn/t1/manifest.json" | grep -q segments               && pass "CDN (borde)"
echo "Resiliencia: deteniendo catalog..."
docker compose stop catalog >/dev/null
curl -fsS "$BASE/api/recs/p-nuevo" | grep -q fallback                   && pass "degradación elegante (fallback)"
docker compose start catalog >/dev/null
echo "Todo correcto."
