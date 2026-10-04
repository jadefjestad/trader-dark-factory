import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("guard", Path(__file__).parent.parent / "scripts" / "guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def test_live_endpoint_regex():
    assert guard.LIVE.search("https://" + "api" + ".alpaca.markets/v2")
    assert not guard.LIVE.search("https://paper-api.alpaca.markets/v2")
    assert not guard.LIVE.search("https://data.alpaca.markets/v2")


def test_repo_passes_guard():
    assert guard.check_live_endpoints() == []
    assert guard.check_candidates() == []
