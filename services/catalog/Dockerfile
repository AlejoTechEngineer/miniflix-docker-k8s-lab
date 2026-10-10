# ---------- Etapa 1: construcción de dependencias ----------
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Etapa 2: imagen de ejecución mínima ----------
FROM python:3.12-slim
LABEL org.opencontainers.image.title="miniflix-service" \
      org.opencontainers.image.description="Microservicio Mini-Flix (laboratorio Unidad 1)"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=builder /install /usr/local
WORKDIR /app
COPY app.py .
# Mínimo privilegio: el proceso no se ejecuta como root
RUN useradd --uid 10001 --no-create-home appuser
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=2s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
