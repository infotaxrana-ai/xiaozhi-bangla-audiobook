"""Build the ESP32-facing Bangla audiobook feed.

The JSON shape mirrors xiaozhi-bangla-podcast/data/podcast_device.json.
Only direct HTTPS MP3/AAC/MP4/M4A enclosures are included. Source bitrate and
actual device playback remain unverified until tested on the board.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ALLOWED_MIME = {"audio/mpeg", "audio/mp3", "audio/mp4", "audio/aac", "audio/x-m4a", "audio/m4a"}
ALLOWED_EXT = {".mp3", ".mp4", ".m4a", ".aac"}


def load_items(data_dir: Path) -> list[dict]:
    items = []
    # Curated catalog comes last so it overrides duplicate imported metadata.
    for filename in ("podcast-import.json", "commons-import.json", "catalog.json"):
        path = data_dir / filename
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                raise ValueError(f"Catalog root must be a JSON array: {path}")
            items.extend(x for x in payload if isinstance(x, dict))
    unique = {}
    for item in items:
        url = str(item.get("audio_url") or "").strip()
        if url:
            unique[url] = item
    return list(unique.values())


def is_device_candidate(item: dict) -> bool:
    url = str(item.get("audio_url") or "").strip()
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return False
    mime = str(item.get("mime_type") or item.get("audio_type") or "").lower().split(";")[0].strip()
    ext = Path(parsed.path).suffix.lower()
    return mime in ALLOWED_MIME or ext in ALLOWED_EXT


def category_for(item: dict) -> str:
    category = str(item.get("category") or "podcast").lower()
    tags = " ".join(str(x) for x in item.get("tags", [])).casefold()
    text = f"{category} {tags}".casefold()
    if any(x in text for x in ("কবিতা", "আবৃত্তি", "poetry", "recitation")):
        return "recitation"
    if any(x in text for x in ("উপন্যাস", "অডিওবুক", "audiobook", "novel")):
        return "audiobook"
    if any(x in text for x in ("গল্প", "story", "golpo")):
        return "story"
    return category


def build(data_dir: Path = DATA, output: Path | None = None) -> dict:
    candidates = [x for x in load_items(data_dir) if is_device_candidate(x)]
    candidates.sort(key=lambda x: (
        str(x.get("author") or "").casefold(),
        str(x.get("title") or "").casefold(),
        str(x.get("id") or ""),
    ))
    episodes = []
    for item in candidates:
        episode = {
            "title": str(item.get("title") or "Untitled audio").strip(),
            "category": category_for(item),
            "audio_url": str(item["audio_url"]).strip(),
        }
        # Optional metadata keeps the author catalogue while preserving the
        # three required fields used by the existing Sunday Suspense feed.
        for key in ("id", "author", "performer", "source_id"):
            if item.get(key):
                episode[key] = item[key]
        episodes.append(episode)

    result = {
        "target_bitrate_kbps": 48,
        "episodes": episodes,
        "schema_version": 1,
        "total": len(episodes),
        "bitrate_verified": False,
        "mode": "audiobook",
        "playback_verified": False,
    }
    target = output or (data_dir / "audiobook_device.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("AUDIOBOOK DEVICE FEED BUILD PASS")
    print("Episodes:", len(episodes))
    print("Target bitrate: 48 kbps (target only; source bitrate not measured)")
    print("Bitrate verified: false")
    print("Playback verified: false (requires board test)")
    return result


if __name__ == "__main__":
    build()
