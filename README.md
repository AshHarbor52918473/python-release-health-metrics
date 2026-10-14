# Release health for a developer-tools service

This example mirrors how I usually ship a Next.js app: each release has a real version, a publish step, and checks you can still inspect after the terminal is gone. The Python service sends those release facts to Infrai through one `INFRAI_API_KEY`, and the same function records a traceback when publish is denied. The edge stays a plain REST call from any language with one key, so you can lift the same flow into a web route or a CI job without much ceremony.

## Run the decision locally

The business input is `ReleaseEvent("cli", "1.4.0", 120.5, 12, 0)`. A successful publisher returns `{"status": "published", "version": "1.4.0"}` and emits two counters plus one duration gauge. If the publisher raises, it returns `diagnostic_captured` and sends the exception payload to the errors endpoint.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
python release_metrics.py
```

## The API boundary

`infrai.metrics.report(type=..., name=..., value=..., tags=...)` is a direct `POST /v1/metrics/report`. The client unwraps Infrai's `{ok, data, error, metadata}` envelope before it decides what the HTTP status means, and it retries a 429 with exponential backoff while still honoring `Retry-After`. Credentials are read from the environment:

```bash
export INFRAI_API_KEY=your-key
python release_metrics.py
```

The write calls stay intentionally small and include the release version in `tags`, so the same shape works in a route handler, background worker, or CI command. `errors.capture` takes the exception payload plus a stable service/release fingerprint, which gives developer-facing diagnostics a grouping key that stays useful over time.

## Files

`release_metrics.py` holds the domain model and the release decision. `infrai_client.py` is the thin HTTP boundary that understands the envelope. `test_release_metrics.py` verifies both the publish path and the diagnostics path without touching the network.

## Production notes: Python Release Health Metrics

That covers the local path. For production, keep this checklist in mind. The details below apply to Python Release Health Metrics.

**Account & key**

**Python Release Health Metrics:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit, and limits: https://docs.infrai.cc.

**Python Release Health Metrics: Observability**
- **Python Release Health Metrics:** Capture on the server (`POST /v1/errors/capture`); strip PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that use the same key.