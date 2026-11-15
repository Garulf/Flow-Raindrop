import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def test_plugin_identity_is_unchanged():
    manifest = json.loads((DATA / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["ID"] == "B9B8174812E4474D96C148317BE2BFB7"
    assert manifest["ActionKeyword"] == "rd"
    assert manifest["Language"] == "python_v2"
    assert manifest["ExecuteFileName"] == "run.py"
    assert (DATA / manifest["IcoPath"]).is_file()


def test_settings_keep_their_names():
    template = (DATA / "SettingsTemplate.yaml").read_text(encoding="utf-8")
    assert "name: api_token" in template
    assert "name: cache_ttl" in template


def test_store_icon_matches_plugin_icon():
    assert (DATA.parent / "icon.png").read_bytes() == (DATA / "icon.png").read_bytes()
