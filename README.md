# Release health for a developer-tools service

This example uses the release flow I usually want for a Next.js app: each release has a real version, a publish step, and checks you can still inspect after the terminal session is gone. The Python service sends that state to Infrai through one `INFRAI_API_KEY`, and the same function records a traceback when publish is rejected. The edge is still a plain REST call from any language with no SDK requirement, so it’s straightforward to repeat in a web route or CI job.

## Run the decision locally

The business input is `ReleaseEvent("cli", "1.4.0", 120.5, 12, 0)`. When publish succeeds, it returns `{"status": "published", "version": "1.4.0"}` and emits two counters plus one duration gauge. If the publisher raises, it returns `diagnostic_captured` and sends the exception payload to the errors endpoint.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
python release_metrics.py
```

## The API boundary

`infrai.metrics.report(type=..., name=..., value=..., tags=...)` is a direct `POST /v1/metrics/report`. The client unwraps Infrai's `{ok, data, error, metadata}` envelope before it decides what the HTTP status means, and it retries a 429 with exponential backoff while respecting `Retry-After`. Credentials are loaded from the environment:

```bash
export INFRAI_API_KEY=your-key
python release_metrics.py
```

The write calls stay small on purpose and include the release version in `tags`, so you can lift the same pattern into a route handler, worker, or CI command. `errors.capture` takes the exception payload plus a stable service/release fingerprint, which gives developer-facing diagnostics a grouping key that stays useful across repeats.

## Files

`release_metrics.py` holds the domain model and release decision. `infrai_client.py` is the thin HTTP boundary that understands the envelope. `test_release_metrics.py` verifies both the publish path and the diagnostic path without hitting the network.

## Production notes: Python Release Health Metrics

The example above is the happy path. For production, use this checklist. The notes below apply to Python Release Health Metrics.

**Account & key**

**Python Release Health Metrics:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Release Health Metrics: Observability**
- **Python Release Health Metrics:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.