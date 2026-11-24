"""pingboard - a tiny uptime-check API used for the CloudAid DevOps challenge."""
import os
import time

from flask import Flask, jsonify, request

STARTED_AT = time.time()

CHECKS = [
    {"name": "api-gateway", "region": "ca-central-1", "status": "up", "latency_ms": 85},
    {"name": "auth", "region": "us-east-1", "status": "up", "latency_ms": 120},
    {"name": "billing-worker", "region": "eu-central-1", "status": "degraded", "latency_ms": 1200},
    {"name": "search-indexer", "region": "us-west-2", "status": "down", "latency_ms": None},
]


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        return jsonify(
            name="pingboard",
            version=os.environ.get("APP_VERSION", "dev"),
            env=os.environ.get("APP_ENV", "development"),
        )

    @app.get("/healthz")
    def healthz():
        # Liveness: the process is up and able to answer HTTP.
        return jsonify(status="ok")

    @app.get("/readyz")
    def readyz():
        # Readiness: the app needs a warm-up period before it can take traffic.
        delay = float(os.environ.get("STARTUP_DELAY_SECONDS", "0"))
        if time.time() - STARTED_AT < delay:
            return jsonify(status="starting"), 503
        return jsonify(status="ready")

    @app.get("/api/checks")
    def checks():
        token = os.environ.get("API_TOKEN", "")
        header = request.headers.get("Authorization", "")
        if not token or header != f"Bearer {token}":
            return jsonify(error="unauthorized"), 403
        return jsonify(checks=CHECKS)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), debug=True)
