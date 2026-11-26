"""Import reusable Bengali audio from Wikimedia Commons with license metadata.

Run: python scripts/import_commons.py
This script uses the Commons API, records original-file URLs and preserves
source, author, license and attribution metadata. Review generated entries.
"""
from __future__ import annotations
import json
import re
import time
from pathlib import Path
from urllib.parse import unquote
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "commons-import.json"
API = "https://commons.wikimedia.org/w/api.php"
CATEGORIES = ["Category:Audiobooks in Bengali", "Category:Spoken Wikisource - Bengali", "Category:LibriVox recordings in Bengali", "Category:Audio files in Bengali"]
HEADERS = {"User-Agent": "XiaozhiBanglaAudioLibrary/0.1 (catalog importer; contact repo maintainer)"}
ALLOWED = {"CC BY 4.0", "CC BY-SA 4.0", "CC BY 3.0", "CC BY-SA 3.0",
           "CC0", "Public domain"}

def clean(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value or "").strip()

def main() -> None:
    session = requests.Session()
    session.headers.update(HEADERS)
    results = []
    for category in CATEGORIES:
      params = {"action":"query","generator":"categorymembers","gcmtitle":category,
                "gcmtype":"file","gcmlimit":"max","prop":"imageinfo",
                "iiprop":"url|extmetadata","iiurlwidth":"0","format":"json"}
      while True:
        response = session.get(API, params=params, timeout=40)
        response.raise_for_status()
        payload = response.json()
        for page in payload.get("query", {}).get("pages", {}).values():
            title = page.get("title", "")
            info = (page.get("imageinfo") or [{}])[0]
            url = info.get("url", "")
            if not url.startswith("https://") or not re.search(r"\.(ogg|oga|mp3|wav|flac|opus)$", url, re.I):
                continue
            meta = info.get("extmetadata", {})
            license_name = clean(meta.get("LicenseShortName", {}).get("value", ""))
            if not any(x.lower() in license_name.lower() for x in ALLOWED):
                continue
            description = clean(meta.get("ImageDescription", {}).get("value", ""))
            artist = clean(meta.get("Artist", {}).get("value", ""))
            creator = clean(meta.get("Credit", {}).get("value", ""))
            source_page = "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_")
            base = title.removeprefix("File:")
            stem = re.sub(r"\.(ogg|oga|mp3|wav|flac|opus)$", "", base, flags=re.I)
            author = stem.split(" - ")[-1] if " - " in stem else ""
            item_id = re.sub(r"[^a-z0-9]+", "-", unquote(stem).lower()).strip("-")
            results.append({
                "id": "commons-" + item_id,
                "title": stem.split(" - ")[0],
                "author": author,
                "performer": artist or creator,
                "category": "audiobook",
                "language": "bn",
                "description": description,
                "audio_url": url,
                "source_url": source_page,
                "license": license_name,
                "license_verified": True,
                "mime_type": info.get("mime", ""),
                "rights_note": "License metadata was read from Wikimedia Commons. Preserve file-page attribution and comply with the listed license.",
                "verified": False,
                "verified_by": None,
                "verification_notice": "License metadata found; direct streaming and audio decoding still require a separate playback test.",
                "tags": ["বাংলা সাহিত্য", "Wikimedia Commons"]
            })
        if "continue" not in payload:
            break
        params.update(payload["continue"])
        time.sleep(0.2)
    # Deduplicate by stable Commons file URL.
    unique = {item["audio_url"]: item for item in results}
    OUT.write_text(json.dumps(list(unique.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(unique)} license-screened audio records to {OUT}")
    print("Imported entries are NOT marked playable until direct streaming is tested and verified=true is set.")

if __name__ == "__main__":
    main()
