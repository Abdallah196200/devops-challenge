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
- Kubernetes: matching labels/selectors, named port, startup/liveness/readiness probes (readiness uses `/readyz`), token from a Secret created at deploy time (no secret committed), 2 replicas, resource requests/limits, non-root, read-only root FS, dropped capabilities, `IfNotPresent`.

## How I verified it
- Locally: `pytest` 5 passed, `flake8` clean, app under gunicorn: `/healthz` 200, `/api/checks` 401 without token and 200 with it.
- In GitHub Actions on this branch (jobs: test, image, k8s): lint and tests pass; `docker build` succeeds and a smoke test of the container passes; a kind cluster deploys the manifests, both pods become Ready with 0 restarts, `/healthz` and token-protected `/api/checks` answer through `kubectl port-forward`.
- Two bugs only showed up when the cluster ran (see history): pods never became Ready because gunicorn needs a writable `/tmp` with a read-only root filesystem (fixed with an emptyDir), and my restart-count check used `bc`, which the runner does not have.

Commands to reproduce on kind:
    docker build -t pingboard:1.0.0 .
    kind create cluster && kind load docker-image pingboard:1.0.0
    kubectl create secret generic pingboard --from-literal=API_TOKEN=dev-token
    kubectl apply -f k8s/
    kubectl rollout status deploy/pingboard
    kubectl port-forward svc/pingboard 8080:80
    curl localhost:8080/healthz
    curl -H "Authorization: Bearer dev-token" localhost:8080/api/checks

## What I left out, and what I would do next
- The Secret is created by hand (no secret in git); production needs sealed/external secrets.
- Pin the base image by digest, add image scanning in CI, HPA, PodDisruptionBudget, NetworkPolicy, a pinned-version bot.

## Tools and time
- Time spent: about 20 minutes of AI assistant work (25 Nov 2026, 12:48 to 13:08 Cairo time): reading the repo, fixing, and iterating on CI until it was green. This is the assistant's elapsed time, not a human's.
- Tools: an AI assistant (Instinct) did the investigation, the fixes, the CI work and the testing (local pytest/flake8/gunicorn, then GitHub Actions with Docker and kind). The submitter has not yet reviewed these changes line by line as of this commit.
