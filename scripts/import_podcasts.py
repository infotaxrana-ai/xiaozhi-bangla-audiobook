"""Import public Bengali podcast RSS enclosures as direct-link candidates.

The audio is not rehosted. RSS records stay unverified until source terms,
media response, bitrate and actual Xiaozhi board playback have been checked.
"""
from __future__ import annotations
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "sources.json"
OUT = ROOT / "data" / "podcast-import.json"
HEADERS = {"User-Agent": "XiaozhiBanglaAudioLibrary/0.3 (+https://github.com/infotaxrana-ai/xiaozhi-bangla-audiobook)"}


def text(node, path, ns):
    found = node.find(path, ns)
    return (found.text or "").strip() if found is not None else ""


def main():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    session = requests.Session()
    session.headers.update(HEADERS)
    imported = []
    feed_status = []
    successful_feeds = 0

    for source in registry["sources"]:
        if source["kind"] != "rss":
            continue
        try:
            response = session.get(source["feed_url"], timeout=35)
            response.raise_for_status()
            root = ET.fromstring(response.content)
        except Exception as exc:
            feed_status.append({"source": source["id"], "status": "error", "error": type(exc).__name__})
            continue

        channel = root.find("channel")
        if channel is None:
            feed_status.append({"source": source["id"], "status": "no_channel"})
            continue
        successful_feeds += 1
        source_count = 0
        ns = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
              "content": "http://purl.org/rss/1.0/modules/content/"}

        for item in channel.findall("item"):
            title = text(item, "title", ns)
            desc = text(item, "description", ns) or text(item, "content:encoded", ns)
            enclosure = item.find("enclosure")
            if enclosure is None:
                continue
            media_url = enclosure.attrib.get("url", "").strip()
            mime = enclosure.attrib.get("type", "").lower().split(";")[0].strip()
            parsed = urlparse(media_url)
            if parsed.scheme != "https" or not parsed.hostname:
                continue
            if mime and not mime.startswith("audio/"):
                continue
            guid = text(item, "guid", ns) or media_url
            stable = hashlib.sha1((source["id"] + "|" + guid).encode()).hexdigest()[:16]
            source_count += 1
            imported.append({
                "id": "pod-" + stable,
                "title": title or "Untitled episode",
                "author": text(channel, "itunes:author", ns) or source["name"],
                "performer": source["name"],
                "category": "podcast",
                "language": source.get("language", "bn"),
                "description": re.sub(r"<[^>]+>", " ", desc)[:1200],
                "audio_url": media_url,
                "source_url": source["website_url"],
                "feed_url": source["feed_url"],
                "source_id": source["id"],
                "mime_type": mime,
                "duration": text(item, "itunes:duration", ns),
                "rights_note": "Public RSS enclosure link; audio is not rehosted. Respect publisher terms and attribution.",
                "license_verified": False,
                "verified": False,
                "device_verified": False,
                "verified_by": None,
                "verification_notice": "RSS enclosure discovered; source bitrate and ESP32 playback are not verified.",
                "tags": source.get("focus", []) + ["podcast"]
            })
        feed_status.append({"source": source["id"], "status": "fetched", "episodes": source_count})

    if successful_feeds == 0:
        print("WARNING: No RSS feed fetched successfully; preserving the previous import file.")
        print(json.dumps(feed_status, ensure_ascii=False))
        return

    unique = {x["id"]: x for x in imported}
    OUT.write_text(json.dumps(list(unique.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(unique)} unverified episodes from {successful_feeds} successful RSS feeds to {OUT}")
    print(json.dumps(feed_status, ensure_ascii=False))
    print("RSS links are direct-link candidates; bitrate and device playback are not asserted.")


if __name__ == "__main__":
    main()
