FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Runtime deps only, installed first so this layer is cached.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as an unprivileged user.
RUN useradd --system --uid 10001 --no-create-home appuser
USER 10001

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import os,urllib.request;urllib.request.urlopen('http://127.0.0.1:%s/healthz' % os.environ.get('PORT','8080'),timeout=2)"

# API_TOKEN is NOT baked in: pass it at runtime (-e API_TOKEN=... or a k8s Secret).
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --access-logfile - app.main:app"]
