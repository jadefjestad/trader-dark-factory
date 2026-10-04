from factory import sources


def test_probe_never_raises(monkeypatch):
    def boom(*a, **k):
        raise ConnectionError("no network")
    monkeypatch.setattr(sources, "_get", boom)
    res = sources.probe()
    assert set(res) == {"alpaca_news", "sec_edgar", "fred"}
    assert all("error" in v for v in res.values())


def test_sec_headers_prepend_app_name(monkeypatch):
    monkeypatch.setenv("SEC_USER_AGENT", "someone@example.com")
    assert sources.sec_headers()["User-Agent"] == "Trader Dark Factory someone@example.com"
    monkeypatch.setenv("SEC_USER_AGENT", "My App someone@example.com")
    assert sources.sec_headers()["User-Agent"] == "My App someone@example.com"


def test_sec_headers_require_secret(monkeypatch):
    import pytest
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    with pytest.raises(RuntimeError):
        sources.sec_headers()
