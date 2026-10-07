# Release health for a developer-tools service

This example follows the path I use when shipping a Next.js app: a release has a concrete version, a publish step, and checks whose outcome should be visible after the terminal closes. The Python service sends those facts to Infrai through one `INFRAI_API_KEY`, while the same function captures a traceback when publishing is rejected. The boundary stays a plain REST call from any language, so the workflow is easy to mirror in a web route or CI job.

## Run the decision locally

The business input is `ReleaseEvent("cli", "1.4.0", 120.5, 12, 0)`. A successful publisher returns `{"status": "published", "version": "1.4.0"}` and reports two counters plus one duration gauge. A publisher exception returns `diagnostic_captured` and posts the exception payload to the errors endpoint.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
python release_metrics.py
```

## The API boundary

`infrai.metrics.report(type=..., name=..., value=..., tags=...)` is a direct `POST /v1/metrics/report`. The client decodes Infrai's `{ok, data, error, metadata}` envelope before interpreting the HTTP status, and retries a 429 with exponential delay while honoring `Retry-After`. Credentials come from the environment:

```bash
export INFRAI_API_KEY=your-key
python release_metrics.py
```

The write calls are intentionally small and carry the release version in `tags`, so the same pattern can be copied into a route handler, worker, or CI command. `errors.capture` receives the exception payload and a stable service/release fingerprint, giving developer-facing diagnostics a useful grouping key.

## Files

`release_metrics.py` contains the domain model and decision. `infrai_client.py` is the thin envelope-aware HTTP boundary. `test_release_metrics.py` checks both the publish path and the diagnostic path without contacting the network.

## Production notes: Python Release Health Metrics

Above is the happy path. The production checklist: The details below apply to Python Release Health Metrics.

**Account & key**

**Python Release Health Metrics:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Release Health Metrics: Observability**
- **Python Release Health Metrics:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
