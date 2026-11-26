import json
import server

def test_unverified_url_is_not_exposed():
    item = {"id": "x", "audio_url": "https://example.org/audio.mp3", "verified": False}
    result = server.public_item(item)
    assert "audio_url" not in result
    assert result["playable"] is False

def test_verified_http_url_is_playable():
    item = {"id": "x", "audio_url": "https://example.org/audio.mp3", "verified": True}
    assert server.playable(item)
    assert server.public_item(item)["audio_url"].endswith(".mp3")

def test_reject_non_http_url():
    item = {"id": "x", "audio_url": "file:///etc/passwd", "verified": True}
    assert not server.playable(item)

def test_load_catalog_from_temp_file(tmp_path, monkeypatch):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps([{"id": "one"}]), encoding="utf-8")
    monkeypatch.setattr(server, "CATALOG_PATH", path)
    assert server.load_catalog() == [{"id": "one"}]
