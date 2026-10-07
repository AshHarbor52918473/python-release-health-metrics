"""Report a release outcome and capture diagnostics for a developer-tools service."""
import traceback
from dataclasses import dataclass
from typing import Callable

import infrai_client as infrai


@dataclass(frozen=True)
class ReleaseEvent:
    service: str
    version: str
    duration_ms: float
    checks_passed: int
    checks_failed: int


def report_release(event: ReleaseEvent, publish: Callable[[], None]) -> dict:
    """Publish once, then report counters and a duration gauge."""
    try:
        publish()
    except Exception as exc:
        infrai.errors.capture(
            title=f"{event.service} release {event.version} failed",
            message=str(exc),
            level="error",
            exception=traceback.format_exc(),
            fingerprint=[event.service, "release"],
            context={"version": event.version},
        )
        return {"status": "diagnostic_captured", "version": event.version}

    tags = {"service": event.service, "version": event.version}
    infrai.metrics.report(type="counter", name="release.completed", value=1, tags=tags)
    infrai.metrics.report(type="counter", name="release.checks_failed", value=event.checks_failed, tags=tags)
    infrai.metrics.report(type="gauge", name="release.duration_ms", value=event.duration_ms, tags=tags)
    return {"status": "published", "version": event.version}


if __name__ == "__main__":
    event = ReleaseEvent("docs-service", "2026.09.07", 842.0, 18, 0)
    print(report_release(event, lambda: print("published release", event.version)))
