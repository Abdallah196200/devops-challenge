# Notes

## Problems I found
- App: `/api/checks` returned 403 instead of the spec's 401 (2 tests failed); token compared with `!=`; `debug=True` in `__main__`.
- Dockerfile: `python:latest` (unpinned), `API_TOKEN` and `FLASK_DEBUG=1` baked into the image, runs as root, `COPY . .` (tests, git data, k8s in image), dev tools in runtime deps, Flask dev server, `EXPOSE 5000` while the app listens on 8080, no healthcheck.
- CI: there was no `.github/workflows/ci.yml` at all.
- Kubernetes: pod label (`pingboard-api`) did not match the Deployment selector (`pingboard`), so the Deployment was invalid; Service selector (`pingboard-web`) matched nothing; ports 5000 vs app 8080; liveness probe on `/health` (app has `/healthz`) with `failureThreshold: 1` and 1s delay, which would restart the pod during the 10s startup; no readiness probe; `imagePullPolicy: Always` on a local image; plaintext token in the manifest; no resources, runs as root.

## What I changed and why
- App: 401 for missing/wrong token, `hmac.compare_digest`, debug off. Behaviour otherwise matches the README table.
- Dockerfile: `python:3.12-slim`, deps installed before code for caching, only `app/` copied, non-root uid 10001, gunicorn, HEALTHCHECK, no secret (token passed at runtime). Runtime and dev requirements split and pinned.
- CI: lint (flake8) and pytest on push and PR, then image build plus a smoke test (healthz 200, checks 401 without token, 200 with token). Fails on any lint or test failure.
- Kubernetes: matching labels/selectors, named port, startup/liveness/readiness probes (readiness uses `/readyz`), token from a Secret, 2 replicas, resource requests/limits, non-root, read-only root FS, dropped capabilities, `IfNotPresent`.

## How I verified it
- `pytest`: 5 passed. `flake8`: clean. Ran the app under gunicorn locally: healthz ok, checks 401/200 as expected.
- NOT YET RUN: `docker build`, GitHub Actions run, kind cluster deploy. (To fill in before submitting.)

Commands to run on kind:
    docker build -t pingboard:1.0.0 .
    kind create cluster && kind load docker-image pingboard:1.0.0
    kubectl apply -f k8s/
    kubectl rollout status deploy/pingboard
    kubectl port-forward svc/pingboard 8080:80
    curl localhost:8080/healthz
    curl -H "Authorization: Bearer dev-token" localhost:8080/api/checks

## What I left out, and what I would do next
- The Secret in `k8s/secret.yaml` is a demo value; production needs sealed/external secrets.
- Pin the base image by digest, add image scanning in CI, HPA, PodDisruptionBudget, NetworkPolicy, a pinned-version bot.

## Tools and time
- Time spent: [to fill in honestly by Abdallah].
- Tools: AI assistant (Instinct) did the investigation and drafting of the changes; Abdallah to review and understand them before submitting.
