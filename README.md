# Xiaozhi Bangla Audio Library

A lightweight MCP service that lets a Xiaozhi voice assistant discover and play Bangla literary audio from direct, rights-respecting audio URLs.

> Status: Author catalog and RSS/Commons importers are implemented. An ESP32-facing static JSON feed is generated in the same compact shape as the existing Sunday Suspense device feed. Source bitrate and actual board playback remain unverified until tested on the device.

## Features

- Static device feed: `data/audiobook_device.json`, matching the existing Xiaozhi podcast feed fields (`target_bitrate_kbps`, `episodes`, `title`, `category`, `audio_url`).
- Weekly GitHub Actions refresh from configured public RSS feeds.
- Device feed includes direct HTTPS MP3/AAC/MP4/M4A links only; untested OGG/OGA candidates are excluded.
- 48 kbps is a device target only; the feed does not claim that source streams are actually 48 kbps.

- Search Bengali audiobook, story, podcast and poetry-recitation entries.
- Return direct audio URLs only for catalog entries marked `verified`.
- Add and maintain your own catalog in `data/catalog.json`.
- Expose MCP tools for Xiaozhi: `search_bangla_audio`, `get_audio_item`, `list_audio_categories`, and `get_catalog_status`.
- Supports HTTP(S) audio URLs and optional feed metadata.

## Quick start

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python server.py
```

The MCP server uses stdio by default, matching the Xiaozhi `mcp_pipe.py` pattern. Configure `MCP_ENDPOINT` with the MCP endpoint URL shown by your Xiaozhi server, then run:

```bash
python mcp_pipe.py server.py
```

The pipe script is intentionally not copied here; use the upstream Xiaozhi server's supported MCP endpoint runner or the upstream `mcp_pipe.py` from its integration example. This repo provides the MCP tool server itself.

## Catalog format

See `data/catalog.example.json`. Each item includes title, author/performer, category, language, audio URL, source URL, rights note and verification status. Run `python scripts/import_commons.py` to fetch license-screened Bengali audio from four Wikimedia Commons collections into `data/commons-import.json`. Run `python scripts/import_podcasts.py` to import episode enclosure URLs from the six configured public RSS feeds into `data/podcast-import.json`; review the generated file before merging records into the main catalog. Only `verified: true` items are exposed as playable results. Commons- and podcast-imported items include original media URLs and source metadata, but are intentionally marked unverified and are not returned as playable until direct streaming and device playback are tested. See `docs/AUDIO_VERIFICATION.md`. Do not add scraped, paywalled, pirated or unauthorized recordings.

## ESP32 static feed

The device feed is published at [`data/audiobook_device.json`](data/audiobook_device.json). Its structure mirrors [`xiaozhi-bangla-podcast/data/podcast_device.json`](https://github.com/infotaxrana-ai/xiaozhi-bangla-podcast/blob/main/data/podcast_device.json). Raw URL: `https://raw.githubusercontent.com/infotaxrana-ai/xiaozhi-bangla-audiobook/main/data/audiobook_device.json`.

RSS enclosure URLs are linked directly; audio is not rehosted. `target_bitrate_kbps: 48` is a target, not a measured source bitrate. `bitrate_verified` and `playback_verified` stay false until the actual stream and ESP32 playback are tested. The installed board firmware must already have an audiobook/feed slot configured to read this URL; this repository does not modify or flash installed firmware.

## Important Xiaozhi playback note

MCP tool integration makes the catalog searchable, but does not guarantee that every Xiaozhi firmware can play an arbitrary URL. Actual playback requires the Xiaozhi server/firmware to support a playback tool or URL-to-audio pipeline. This project returns a URL and metadata; it does not pretend that the ESP32 can stream every codec/container directly. Prefer MP3/AAC streams supported by your server's playback implementation.

## Add audio

1. Confirm that the provider publishes a stable direct audio URL (not a webpage/player page).
2. Confirm that linking/streaming is permitted by the provider and applicable rights.
3. Add the item to `data/catalog.json` and set `verified` to `true` only after testing the URL with an HTTP client/player.
4. Restart the MCP server.

## Development and tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

GitHub Actions runs the test suite on pushes to `main` and pull requests.

## License

Project code: MIT. Audio recordings remain owned/licensed by their respective rights holders; this code does not grant rights to any recording.
