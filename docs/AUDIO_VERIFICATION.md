# Audio source and playback verification

A catalog entry has two separate checks:

1. **License/source screening**: record the Commons/provider source page, author or performer, license identifier, and attribution requirements.
2. **Playable verification**: test the actual media URL from the machine running the Xiaozhi server. Confirm that it returns audio bytes (not an HTML page), does not require cookies/login, is not an expiring signed URL, and can be decoded by the server's playback path.

Do not set `verified: true` merely because a file appears in Wikimedia Commons or its license metadata is present. The importer intentionally sets `verified: false`. After testing a candidate URL, set `verified: true` manually and record `verified_by`, `verified_at`, `mime_type`, and a short test note.

Example test commands:

    curl -L -I 'DIRECT_MEDIA_URL'
    curl -L --range 0-1023 -o /tmp/audio-sample 'DIRECT_MEDIA_URL'
    file /tmp/audio-sample

A redirect to `upload.wikimedia.org` can be normal; the final response must be media, not HTML. A successful HTTP response alone does not prove that Xiaozhi's playback implementation supports the codec/container. Test the exact audio through the configured playback tool as a separate end-to-end check.

Keep attribution with every recording. CC BY requires attribution; CC BY-SA additionally requires compatible share-alike terms when distributing adaptations. Follow the exact license shown on the individual file page, not a category-level assumption.
