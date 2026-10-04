from factory import sources


def test_probe_never_raises(monkeypatch):
    def boom(*a, **k):
        raise ConnectionError("no network")
    monkeypatch.setattr(sources, "_get", boom)
    res = sources.probe()
    assert set(res) == {"alpaca_news", "sec_edgar", "fred"}
    assert all("error" in v for v in res.values())
