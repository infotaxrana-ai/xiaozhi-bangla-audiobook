"""Import podcast episodes from the configured public Bengali RSS feeds.

RSS enclosure URLs are stored as unverified. Do not expose as playable until
the media URL, rights and Xiaozhi playback path have been checked.
"""
from __future__ import annotations
import json, re, hashlib
from pathlib import Path
from urllib.parse import urlparse
import requests
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "sources.json"
OUT = ROOT / "data" / "podcast-import.json"
HEADERS = {"User-Agent": "XiaozhiBanglaAudioLibrary/0.2 (+https://github.com/infotaxrana-ai/xiaozhi-bangla-audiobook)"}
AUDIO_TYPES = ("audio/",)

def text(node, path, ns):
    found = node.find(path, ns)
    return (found.text or "").strip() if found is not None else ""

def main():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    session = requests.Session()
    session.headers.update(HEADERS)
    imported = []
    for source in registry["sources"]:
        if source["kind"] != "rss":
            continue
        response = session.get(source["feed_url"], timeout=35)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        ns = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
              "content": "http://purl.org/rss/1.0/modules/content/"}
        channel = root.find("channel")
        if channel is None:
            continue
        for item in channel.findall("item"):
            title = text(item, "title", ns)
            desc = text(item, "description", ns) or text(item, "content:encoded", ns)
            enclosure = item.find("enclosure")
            if enclosure is None:
                continue
            media_url = enclosure.attrib.get("url", "").strip()
            mime = enclosure.attrib.get("type", "").lower()
            if urlparse(media_url).scheme not in ("http", "https") or (mime and not mime.startswith(AUDIO_TYPES)):
                continue
            guid = text(item, "guid", ns) or media_url
            stable = hashlib.sha1((source["id"] + "|" + guid).encode()).hexdigest()[:16]
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
                "rights_note": "Publisher RSS enclosure. Confirm the publisher's reuse/streaming terms before redistributing or exposing as playable.",
                "license_verified": False,
                "verified": False,
                "verified_by": None,
                "verification_notice": "RSS enclosure discovered; media response, reuse rights and Xiaozhi playback are not yet verified.",
                "tags": source.get("focus", []) + ["podcast"]
            })
    unique = {x["id"]: x for x in imported}
    OUT.write_text(json.dumps(list(unique.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(unique)} unverified episodes from {sum(s['kind']=='rss' for s in registry['sources'])} RSS feeds to {OUT}")
    print("No episode is marked playable; verify media, rights and device playback first.")

if __name__ == "__main__":
    main()
