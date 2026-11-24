# CloudAid DevOps Engineer: take-home challenge

Thanks for applying. This is a short, practical exercise that looks like the work
you would do with us: someone hands you a small service whose delivery setup
"mostly works", and you make it production-ready.

- **Time box:** 3 to 4 hours. Please don't spend more. Unfinished parts are fine
  if you explain them in `NOTES.md`.
- **Deadline:** 5 calendar days from the email that sent you here.
- **Cost:** nothing. Everything runs locally and on free GitHub Actions. You do
  not need a cloud account.

## The service

`pingboard` is a tiny Flask API.

| Endpoint          | Behaviour                                                                 |
| ----------------- | ------------------------------------------------------------------------- |
| `GET /`           | Service name, version (`APP_VERSION`), environment (`APP_ENV`)            |
| `GET /healthz`    | Liveness. `200 {"status":"ok"}` whenever the process is up                |
| `GET /readyz`     | Readiness. `503` for the first `STARTUP_DELAY_SECONDS` seconds, then `200` |
| `GET /api/checks` | Needs `Authorization: Bearer <API_TOKEN>`. `200` with data, otherwise **`401`** |

Configuration is by environment variable: `PORT` (default `8080`), `APP_ENV`,
`APP_VERSION`, `STARTUP_DELAY_SECONDS`, `API_TOKEN`.

This table is the spec. Where the code and the table disagree, the table wins.

Run it locally:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
API_TOKEN=dev python app/main.py
pytest
```

## Your task

The `Dockerfile`, the CI workflow and the Kubernetes manifests in this repo all
have deliberate problems. Some stop things from working at all, some only show
up when you actually run them, and some "work" but would not survive a
production review. **Finding them is part of the task, so we don't list them.**

### Part 1: Container

Make the image something you would be comfortable running in production.

Done when: `docker build` succeeds, `docker run` serves `/healthz` on port
`8080`, and neither the image nor the git history you add contains a secret.

### Part 2: CI

Make `.github/workflows/ci.yml` a pipeline you would trust.

Done when: it runs on pushes and pull requests in **your fork**, it goes red
when a test or lint check fails, it goes green on your final commit, and it
builds the image. (Enable Actions in your fork's *Actions* tab first.)

### Part 3: Kubernetes

Make the manifests in `k8s/` deploy cleanly to a fresh local cluster
([kind](https://kind.sigs.k8s.io/) or minikube).

Done when, on a fresh cluster:

```bash
kubectl apply -f k8s/
kubectl rollout status deploy/pingboard
kubectl port-forward svc/pingboard 8080:80
curl localhost:8080/healthz
curl -H "Authorization: Bearer <token>" localhost:8080/api/checks
```

all work, pods become Ready and stay at 0 restarts, and the manifests are what
you would accept in a production review. If your setup needs extra steps
(loading the image into kind, creating a Secret), document the exact commands.

### Part 4: NOTES.md

Fill in `NOTES.md`. We read this first. Keep it short and specific.

### Optional stretch (pick at most one)

Only if you have time left inside the time box: autoscaling, Kustomize or Helm
packaging, image scanning or signing in CI, or a `/metrics` endpoint with a
scrape config. One done well beats three half done.

## Rules

1. **Fork** this repo to your own GitHub account. Work on a branch named
   `solution`.
2. Commit as you go with meaningful messages. We read the history, so please
   don't squash it into one commit.
3. **Do not open a pull request against this repository.** Your fork is your
   submission.
4. Any tools are allowed, including AI assistants. Say what you used in
   `NOTES.md`. In the next interview we will ask you to walk through your
   changes and extend them live, so only submit what you understand.
5. Don't change the API behaviour described in the table above.

## Submitting

Reply to the email that sent you here with:

1. The link to your fork, branch `solution`.
2. A link to a green Actions run on that branch.
3. Roughly how long you spent.

We will reply within 5 working days either way.
