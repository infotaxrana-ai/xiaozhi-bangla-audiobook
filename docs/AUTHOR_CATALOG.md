# Author-wise catalog

The library now has a canonical author/poet directory at `data/authors.json`.
Each entry has a stable ID, Bengali and English display names, searchable aliases,
and broad work categories. The MCP server exposes `list_authors(query)` and
supports author/poet aliases in `search_bangla_audio(author=...)`.

## Important distinction

The directory is an index of writers, not a claim that recordings already exist.
`catalog_item_count` is computed from actual imported/curated catalog metadata.
An author with zero items is listed with a count of zero. Items are associated
only when their author metadata or text explicitly matches a configured alias,
or when a curator sets `author_id` on the record. Do not infer authorship from
the source podcast's name or from an unrelated episode title.

Imported RSS and Commons records remain unverified. The server withholds their
direct audio URLs until media, reuse rights and the configured Xiaozhi playback
path have been checked. Do not mark an item playable merely because its author
is known or its source appears in the directory.

## Included authors

Rabindranath Tagore, Kazi Nazrul Islam, Jibanananda Das, Sukanta Bhattacharya,
Jasimuddin, Michael Madhusudan Dutt, Humayun Ahmed, Sarat Chandra Chattopadhyay,
Bankim Chandra Chattopadhyay and Bibhutibhushan Bandyopadhyay.
