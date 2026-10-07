from release_metrics import ReleaseEvent, report_release


def test_release_success_reports_business_decision(monkeypatch):
    calls = []
    monkeypatch.setattr("release_metrics.infrai.metrics.report", lambda **payload: calls.append(payload))
    result = report_release(ReleaseEvent("cli", "1.4.0", 120.5, 12, 0), lambda: None)
    assert result == {"status": "published", "version": "1.4.0"}
    assert [call["name"] for call in calls] == ["release.completed", "release.checks_failed", "release.duration_ms"]


def test_release_failure_captures_diagnostic(monkeypatch):
    captured = []
    monkeypatch.setattr("release_metrics.infrai.errors.capture", lambda **payload: captured.append(payload))
    result = report_release(ReleaseEvent("web", "2.0.0", 90, 4, 1), lambda: (_ for _ in ()).throw(ValueError("lint")))
    assert result["status"] == "diagnostic_captured"
    assert captured[0]["exception"]
