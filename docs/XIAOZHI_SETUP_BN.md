# Xiaozhi-তে সংযোগ

## এই repository কী করে
এটি একটি MCP tool server। Xiaozhi-এর MCP endpoint-এ যুক্ত হলে voice assistant বাংলা audiobook, গল্পের podcast এবং কবিতা আবৃত্তির ক্যাটালগ খুঁজতে পারবে। MCP ফলাফলে যাচাইকৃত direct audio URL ও metadata পাওয়া যাবে।

**গুরুত্বপূর্ণ:** MCP server যুক্ত হলেই ESP32-তে অডিও বাজবে—এমন নিশ্চয়তা নেই। Xiaozhi server/firmware-এ URL গ্রহণ করে অডিও চালানোর playback tool বা pipeline থাকতে হবে। এই repository catalog search ও URL দেয়; firmware playback তৈরি করে না।

## ১. চালু করুন
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python server.py

Windows PowerShell-এ virtual environment চালু করতে .venv\\Scripts\\Activate.ps1 ব্যবহার করুন।

## ২. Xiaozhi MCP endpoint-এ যুক্ত করুন
Xiaozhi server-এর MCP endpoint integration guide অনুসরণ করুন। Agent-এর MCP endpoint URL কপি করুন; URL-এ token থাকলে সেটি গোপন রাখুন।

Upstream Xiaozhi integration-এর mcp_pipe.py runner ব্যবহার করে:

Linux/macOS:
    export MCP_ENDPOINT='ws://YOUR_SERVER:8004/mcp_endpoint/mcp/?token=YOUR_TOKEN'
    python mcp_pipe.py /path/to/xiaozhi-bangla-audiobook/server.py

Windows PowerShell:
    $env:MCP_ENDPOINT = "ws://YOUR_SERVER:8004/mcp_endpoint/mcp/?token=YOUR_TOKEN"
    python mcp_pipe.py C:\\path\\to\\xiaozhi-bangla-audiobook\\server.py

Xiaozhi control panel-এ MCP status refresh করুন। Tool list-এ search_bangla_audio, get_audio_item, list_audio_categories এবং get_catalog_status দেখা উচিত।

mcp_pipe.py upstream Xiaozhi server project-এর integration runner; এই repository-তে সেটি কপি করা হয়নি। Runner-এর সর্বশেষ নির্দেশনা upstream documentation-এ দেখুন।

## ৩. নিজের catalog যোগ করুন
data/catalog.example.json কপি করে data/catalog.json বানান। প্রতিটি item-এ unique id, title, author/performer, category, direct audio_url, source page এবং rights note দিন।

- audio_url সরাসরি HTTP(S) audio resource হতে হবে; ওয়েব player/page URL নয়।
- URL browser/player-এ পরীক্ষা করুন; redirect, authentication, hotlink protection ও expiry পরীক্ষা করুন।
- Provider-এর terms এবং copyright অনুমতি যাচাই করুন।
- যাচাই শেষে verified: true দিন। অন্যথায় URL MCP response-এ লুকানো থাকবে।
- scraping, DRM bypass, paywall bypass বা অনুমতিহীন recording যোগ করবেন না।

প্রস্তাবিত category: audiobook, golpo, podcast, kobita, recitation, drama।

## ৪. Playback
Assistant-কে বলতে পারেন: “বাংলা কবিতা আবৃত্তি খুঁজে দাও” বা “হুমায়ূন আহমেদের গল্পের অডিও খুঁজে দাও”। Catalog-এ matching item থাকলে MCP search result দেবে। Playback tool থাকলে সেই URL playback tool-এ পাঠাতে হবে। আপনার server-এ playback tool-এর নাম/argument ভিন্ন হলে agent prompt বা adapter অনুযায়ী mapping লাগবে।


## ৫. Wikimedia Commons থেকে আরও অডিও আনুন

প্রথমে dependencies ইনস্টল/আপডেট করুন:

    pip install -r requirements.txt

তারপর চালান:

    python scripts/import_commons.py

স্ক্রিপ্টটি Wikimedia Commons-এর Bengali audiobook category থেকে অডিও ফাইল, direct media URL, author/performer এবং license metadata সংগ্রহ করে `data/commons-import.json` বানাবে। এটি কেবল অনুমোদিত CC BY/CC BY-SA/CC0/Public Domain লাইসেন্স শনাক্ত হওয়া ফাইল নেয়।

এই generated catalog `server.py` স্বয়ংক্রিয়ভাবে load করে। Import শেষে:

    python -c "import server; print(server.get_catalog_status())"

তারপর MCP server restart করুন। কোনো রেকর্ড ব্যবহার বা পুনঃপ্রকাশের আগে source page-এর attribution/license শর্ত দেখে নিন। Wikimedia Commons-এ পাওয়া মানেই সব ফাইল public domain নয়; অনেক recording CC BY-SA লাইসেন্সের।
