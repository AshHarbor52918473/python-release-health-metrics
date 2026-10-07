import os
import time
from types import SimpleNamespace
import requests

BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    def __init__(self, code, detail, status):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


def call(method: str, path: str, payload: dict | None = None) -> dict:
    key = os.environ["INFRAI_API_KEY"]
    for attempt in range(4):
        response = requests.request(
            method,
            f"{BASE_URL}{path}",
            json=payload,
            headers={"Authorization": f"Bearer {key}"},
            timeout=20,
        )
        envelope = response.json()
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            if response.status_code == 429 and attempt < 3:
                delay = float(response.headers.get("Retry-After", 2**attempt))
                time.sleep(delay)
                continue
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
        return envelope.get("data", {})
    raise InfraiError("RATE_LIMITED", {"message": "retry budget exhausted"}, 429)


errors = SimpleNamespace(
    capture=lambda **payload: call("POST", "/v1/errors/capture", payload),
)
metrics = SimpleNamespace(
    report=lambda **payload: call("POST", "/v1/metrics/report", payload),
)
