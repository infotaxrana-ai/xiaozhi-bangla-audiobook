# Source integration status

The registry contains ten source endpoints: six public podcast RSS feeds and four Wikimedia Commons category endpoints. These are not ten unrelated hosting companies; the Commons categories are separate discovery collections on one provider.

## Podcast feeds
- **Roll Sound: Goppo** — [RSS](https://anchor.fm/s/101ce3cd4/podcast/rss) — বাংলা গল্প, গল্পপাঠ
- **গল্প-কথার আসর** — [RSS](https://rss.buzzsprout.com/1194824.rss) — বাংলা সাহিত্য, গল্প, উপন্যাস
- **Upokotha – Bengali Audio Stories** — [RSS](https://anchor.fm/s/119e31f60/podcast/rss) — রবীন্দ্রনাথ, শরৎচন্দ্র, গল্প
- **Bengali Poetry Recitation and Audio Book** — [RSS](https://anchor.fm/s/117d788b4/podcast/rss) — কবিতা, আবৃত্তি, অডিওবুক
- **Story Nights with Babon** — [RSS](https://anchor.fm/s/615808e8/podcast/rss) — বাংলা অডিও গল্প
- **অপদার্থের রোজনামচা** — [RSS](https://www.spreaker.com/show/6593287/episodes/feed) — গল্প, কবিতা

## Open Wikimedia Commons collections
- **Wikimedia Commons – Bengali Audiobooks** — [collection](https://commons.wikimedia.org/wiki/Category:Audiobooks_in_Bengali)
- **Wikimedia Commons – Spoken Wikisource Bengali** — [collection](https://commons.wikimedia.org/wiki/Category:Spoken_Wikisource_-_Bengali)
- **Wikimedia Commons – LibriVox Bengali** — [collection](https://commons.wikimedia.org/wiki/Category:LibriVox_recordings_in_Bengali)
- **Wikimedia Commons – Audio files in Bengali** — [collection](https://commons.wikimedia.org/wiki/Category:Audio_files_in_Bengali)

## Import and playback safety
Run `python scripts/import_podcasts.py` to fetch RSS enclosures into `data/podcast-import.json`. The importer only reads public RSS XML and records direct enclosure URLs; it does not bypass paywalls or download audio files. All imported records remain `verified: false`. The Xiaozhi MCP server must not return them as playable until the actual HTTP response contains audio, provider terms permit streaming, and the configured Xiaozhi playback tool successfully plays the item.

The Commons importer currently scans the Bengali audiobook category. The additional Commons categories are registered for the next importer extension and are not yet harvested by the existing script.
