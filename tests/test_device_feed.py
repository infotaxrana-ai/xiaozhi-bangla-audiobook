import json
from pathlib import Path
from scripts.build_device_feed import build


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def test_rss_mp3_is_exported_in_sunday_suspense_device_shape(tmp_path):
    data = tmp_path / "data"
    write_json(data / "podcast-import.json", [{
        "id": "pod-1", "title": "হুমায়ূন আহমেদের গল্প",
        "author": "হুমায়ূন আহমেদ", "category": "podcast",
        "source_id": "golpo-kothar-asor", "tags": ["অডিওবুক"], "mime_type": "audio/mpeg",
        "audio_url": "https://cdn.example.org/story.mp3", "verified": False,
    }])
    result = build(data, data / "audiobook_device.json")
    assert result["total"] == 1
    assert result["target_bitrate_kbps"] == 48
    assert result["bitrate_verified"] is False
    assert result["playback_verified"] is False
    episode = result["episodes"][0]
    assert episode["title"] == "হুমায়ূন আহমেদের গল্প"
    assert episode["author"] == "হুমায়ূন আহমেদ"
    assert episode["audio_url"] == "https://cdn.example.org/story.mp3"
    assert episode["category"] == "audiobook"


def test_unverified_ogg_and_http_urls_are_not_added(tmp_path):
    data = tmp_path / "data"
    write_json(data / "catalog.json", [
        {"id": "ogg", "title": "OGG", "audio_url": "https://cdn.example.org/a.ogg",
         "mime_type": "audio/ogg", "verified": False},
        {"id": "http", "title": "HTTP", "audio_url": "http://cdn.example.org/a.mp3",
         "mime_type": "audio/mpeg", "verified": True},
    ])
    result = build(data, data / "audiobook_device.json")
    assert result["total"] == 0
    assert result["episodes"] == []


def test_curated_mp4_overrides_duplicate_rss_record(tmp_path):
    data = tmp_path / "data"
    url = "https://cdn.example.org/book.mp4"
    write_json(data / "podcast-import.json", [
        {"id": "rss", "title": "RSS copy", "audio_url": url, "mime_type": "audio/mp4",
         "source_id": "story-feed"}
    ])
    write_json(data / "catalog.json", [
        {"id": "curated", "title": "Curated title", "author": "লেখক",
         "audio_url": url, "mime_type": "audio/mp4", "verified": True}
    ])
    result = build(data, data / "audiobook_device.json")
    assert result["total"] == 1
    assert result["episodes"][0]["title"] == "Curated title"
    assert result["episodes"][0]["author"] == "লেখক"


def test_poetry_category_is_normalized(tmp_path):
    data = tmp_path / "data"
    write_json(data / "catalog.json", [{
        "id": "poem", "title": "কবিতা আবৃত্তি", "category": "recitation",
        "tags": ["কবিতা", "আবৃত্তি"], "audio_url": "https://cdn.example.org/poem.mp3",
        "mime_type": "audio/mpeg", "verified": True,
    }])
    result = build(data, data / "audiobook_device.json")
    assert result["episodes"][0]["category"] == "recitation"
