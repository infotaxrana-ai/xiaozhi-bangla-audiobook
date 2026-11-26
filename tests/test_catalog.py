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


def test_reject_missing_audio_url():
    assert not server.playable({"id": "x", "verified": True})


def test_load_catalog_from_temp_file(tmp_path, monkeypatch):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps([{"id": "one"}]), encoding="utf-8")
    monkeypatch.setattr(server, "CATALOG_PATH", path)
    monkeypatch.setattr(server, "ROOT", tmp_path)
    assert server.load_catalog() == [{"id": "one"}]


def test_curated_entry_overrides_imported_duplicate(tmp_path, monkeypatch):
    imported = tmp_path / "data" / "commons-import.json"
    imported.parent.mkdir()
    imported.write_text(json.dumps([
        {"id": "imported", "audio_url": "https://example.org/a.ogg", "title": "Imported"}
    ]), encoding="utf-8")
    curated = tmp_path / "catalog.json"
    curated.write_text(json.dumps([
        {"id": "curated", "audio_url": "https://example.org/a.ogg", "title": "Curated"}
    ]), encoding="utf-8")
    monkeypatch.setattr(server, "ROOT", tmp_path)
    monkeypatch.setattr(server, "CATALOG_PATH", curated)
    assert server.load_catalog()[0]["title"] == "Curated"


def test_author_directory_counts_and_alias_search(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "authors.json").write_text(json.dumps({
        "authors": [
            {"id": "rabindranath-tagore", "name_bn": "রবীন্দ্রনাথ ঠাকুর",
             "name_en": "Rabindranath Tagore", "aliases": ["রবীন্দ্রনাথ", "Tagore"],
             "categories": ["গল্প"]}
        ]
    }, ensure_ascii=False), encoding="utf-8")
    (data_dir / "catalog.json").write_text(json.dumps([
        {"id": "one", "author_id": "rabindranath-tagore", "title": "অতিথি",
         "author": "রবীন্দ্রনাথ ঠাকুর", "verified": False}
    ], ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(server, "ROOT", tmp_path)
    monkeypatch.setattr(server, "CATALOG_PATH", data_dir / "catalog.json")
    result = server.list_authors("Tagore")
    assert result["count"] == 1
    assert result["authors"][0]["catalog_item_count"] == 1
    search = server.search_bangla_audio(author="রবীন্দ্রনাথ")
    assert search["count"] == 1
    assert search["items"][0]["playable"] is False
    assert "audio_url" not in search["items"][0]


def test_author_alias_does_not_match_unrelated_record():
    author = {"id": "rabindranath-tagore", "aliases": ["রবীন্দ্রনাথ", "Tagore"]}
    assert server.author_matches({"title": "অতিথি", "author": "রবীন্দ্রনাথ ঠাকুর"}, author)
    assert not server.author_matches({"title": "পথের পাঁচালী", "author": "বিভূতিভূষণ"}, author)


def test_search_rotates_without_repeating_until_cycle_is_exhausted(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "catalog.json").write_text(json.dumps([
        {"id": "a", "title": "গল্প A", "audio_url": "https://example.org/a.mp3", "verified": True},
        {"id": "b", "title": "গল্প B", "audio_url": "https://example.org/b.mp3", "verified": True},
        {"id": "c", "title": "গল্প C", "audio_url": "https://example.org/c.mp3", "verified": True}
    ], ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(server, "ROOT", tmp_path)
    monkeypatch.setattr(server, "CATALOG_PATH", data_dir / "catalog.json")
    monkeypatch.setattr(server, "AUTHORS_PATH", data_dir / "authors.json")
    monkeypatch.setattr(server.random, "shuffle", lambda values: None)
    server._ROTATION_QUEUES.clear()

    first = server.search_bangla_audio(limit=2)
    second = server.search_bangla_audio(limit=2)
    third = server.search_bangla_audio(limit=2)

    first_ids = [x["id"] for x in first["items"]]
    second_ids = [x["id"] for x in second["items"]]
    third_ids = [x["id"] for x in third["items"]]
    assert first_ids == ["a", "b"]
    assert second_ids == ["c"]
    assert set(first_ids).isdisjoint(second_ids)
    assert third_ids == ["a", "b"]


def test_search_rotation_is_independent_for_different_queries(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "catalog.json").write_text(json.dumps([
        {"id": "a", "title": "গল্প A", "audio_url": "https://example.org/a.mp3", "verified": True},
        {"id": "b", "title": "কবিতা B", "audio_url": "https://example.org/b.mp3", "verified": True}
    ], ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(server, "ROOT", tmp_path)
    monkeypatch.setattr(server, "CATALOG_PATH", data_dir / "catalog.json")
    monkeypatch.setattr(server, "AUTHORS_PATH", data_dir / "authors.json")
    monkeypatch.setattr(server.random, "shuffle", lambda values: None)
    server._ROTATION_QUEUES.clear()

    story = server.search_bangla_audio(query="গল্প", limit=1)
    poem = server.search_bangla_audio(query="কবিতা", limit=1)
    assert story["items"][0]["id"] == "a"
    assert poem["items"][0]["id"] == "b"
