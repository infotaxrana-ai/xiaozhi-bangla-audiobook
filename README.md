# Xiaozhi Bangla Audio Library

A lightweight MCP service that lets a Xiaozhi voice assistant discover and play Bangla literary audio from direct, rights-respecting audio URLs.

> Status: MCP catalog and Commons importer implemented. Direct playback is deliberately disabled for entries until the exact media URL and Xiaozhi playback path have been tested.

## Features

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

See `data/catalog.example.json`. Each item includes title, author/performer, category, language, audio URL, source URL, rights note and verification status. Run `python scripts/import_commons.py` to fetch currently licensed Bengali audiobook entries from Wikimedia Commons into `data/commons-import.json`; review the generated file before merging records into the main catalog. Only `verified: true` items are exposed as playable results. Commons-imported items include the original media URL and license metadata, but are intentionally marked unverified and are not returned as playable until direct streaming and device playback are tested. See `docs/AUDIO_VERIFICATION.md`. Do not add scraped, paywalled, pirated or unauthorized recordings.

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
