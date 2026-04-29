import re
import json
import requests
import time
from datetime import datetime
from collections import OrderedDict

# لیست کانال‌های هدف (بدون @ یا t.me/ فقط نام کاربری)
CHANNELS = [
    "xgvpn",
    "appxa",
    "appxa2",
    "IRNOTPHONE",
    "IRAN_V2RAY1",
    "SlipNet_decode",
    "blackRay",
    "SparrK_VPN",
    "slipnet_chat",
    "SlipNet_app",
    "VConfing",
    "capcutchina"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# فایل ذخیره داده‌ها
DB_FILE = "slipnet_db.json"
HTML_FILE = "index.html"

# الگوی لینک‌های slipnet
SLIPNET_PATTERN = re.compile(r'slipnet(?:-enc)?:\/\/[^\s<>"\'\[\]{}|\\^`]+', re.IGNORECASE)

def fetch_channel_page(username: str) -> str:
    """دریافت صفحه عمومی کانال تلگرام"""
    url = f"https://t.me/s/{username}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Error fetching {username}: {e}")
        return ""

def extract_links(html: str) -> set:
    """استخراج تمام لینک‌های slipnet از HTML"""
    return set(SLIPNET_PATTERN.findall(html))

def load_existing_db() -> OrderedDict:
    """بارگذاری فایل JSON که حاوی لینک‌ها و زمان اولین مشاهده است"""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # تبدیل به OrderedDict بر اساس ترتیب insertion (قدیمی‌ترین اول)
            # اما می‌خواهیم جدیدترین اول باشد، لذا برعکس می‌کنیم بعداً
            ordered = OrderedDict()
            for link in data.get("links", []):
                ordered[link] = data["timestamps"].get(link, time.time())
            return ordered
    except (FileNotFoundError, json.JSONDecodeError):
        return OrderedDict()

def save_db(links_dict: OrderedDict):
    """ذخیره دیتابیس به صورت JSON با حفظ ترتیب (جدیدترین آخر؟ برای سادگی)"""
    # links_dict: key=link, value=timestamp
    # برای ذخیره، یک لیست از لینک‌ها به ترتیب از جدید به قدیم می‌سازیم
    sorted_links = list(links_dict.keys())  # ترتیب فعلی: new first? بستگی دارد
    # ما در حافظه ترتیب را جدیدترین اول نگه می‌داریم. پس همین را ذخیره کنیم
    data = {
        "links": sorted_links,
        "timestamps": {link: ts for link, ts in links_dict.items()}
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_html(links_list: list, last_update: str) -> str:
    """تولید فایل HTML با لیست لینک‌ها (جدیدترین در بالا)"""
    rows = ""
    for link in links_list:
        rows += f"""
        <div class="config-item">
            <span class="config-link" onclick="copyToClipboard('{link}')" title="Click to copy">{link}</span>
            <button class="copy-btn" onclick="copyToClipboard('{link}')">Copy</button>
        </div>
        """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SlipNet Configs - Live Collector</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            background: #0a0a0a;
            font-family: 'Courier New', monospace;
            padding: 2rem;
            color: #e0e0e0;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        h1 {{
            color: #2AABEE;
            border-left: 4px solid #2AABEE;
            padding-left: 20px;
            margin-bottom: 1rem;
        }}
        .info {{
            background: #111;
            padding: 10px 20px;
            border-radius: 8px;
            margin-bottom: 2rem;
            font-size: 0.85rem;
            color: #aaa;
        }}
        .config-list {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        .config-item {{
            background: #1a1a1a;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 15px;
            border-radius: 6px;
            border-left: 3px solid #2AABEE;
            transition: 0.2s;
            word-break: break-all;
        }}
        .config-item:hover {{
            background: #222;
        }}
        .config-link {{
            font-size: 13px;
            font-family: monospace;
            cursor: pointer;
            flex: 1;
            margin-right: 15px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        .copy-btn {{
            background: #2AABEE20;
            border: 1px solid #2AABEE;
            color: #2AABEE;
            padding: 6px 12px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            cursor: pointer;
            transition: 0.2s;
        }}
        .copy-btn:hover {{
            background: #2AABEE;
            color: #000;
        }}
        footer {{
            margin-top: 3rem;
            text-align: center;
            font-size: 11px;
            color: #444;
        }}
    </style>
    <script>
        function copyToClipboard(text) {{
            navigator.clipboard.writeText(text).then(() => {{
                alert('Copied!');
            }}).catch(() => {{
                prompt('Manual copy:', text);
            }});
        }}
    </script>
</head>
<body>
<div class="container">
    <h1>🔗 SlipNet Collector</h1>
    <div class="info">
        📡 Last update: {last_update}<br>
        📦 Total unique configs: {len(links_list)}<br>
        🔄 Auto-updates every 30 minutes via GitHub Actions
    </div>
    <div class="config-list">
        {rows}
    </div>
    <footer>generated by SHEN collector — slipnet:// & slipnet-enc://</footer>
</div>
</body>
</html>"""
    return html

def main():
    print(f"[{datetime.now().isoformat()}] Starting SlipNet collector...")
    all_new_links = set()

    # مرحله 1: استخراج لینک‌ها از تمام کانال‌ها
    for ch in CHANNELS:
        print(f"  -> Fetching {ch}")
        html = fetch_channel_page(ch)
        if html:
            links = extract_links(html)
            if links:
                print(f"      Found {len(links)} slipnet link(s)")
                all_new_links.update(links)
            else:
                print("      No slipnet links")
        time.sleep(1)  # احترام به محدودیت

    if not all_new_links:
        print("No new links found at all.")
        # هنوز ممکن است db قدیم وجود داشته باشد، اما اگر خالی باشد، خروجی قبلی را حفظ می‌کنیم
    else:
        print(f"Total unique links across channels: {len(all_new_links)}")

    # مرحله 2: بارگذاری دیتابیس قبلی
    existing = load_existing_db()  # OrderedDict به ترتیب جدید→قدیم؟ فعلاً هر ترتیبی که باشد
    # existing: key=link, value=timestamp (اولین مشاهده)
    # اما ترتیب در OrderedDict بر اساس زمان اضافه شدن (قدیمی‌ترین اول) است چون هنگام بارگذاری از لیست JSON به ترتیب اضافه کردیم.
    # برای اینکه جدیدترین‌ها اول باشند، بهتر است پس از ادغام، بر اساس timestamp نزولی مرتب کنیم.

    # ادغام لینک‌های جدید
    now_ts = time.time()
    updated = OrderedDict()
    # ابتدا لینک‌های موجود قبلی را با timestamp خودشان نگه می‌داریم
    for link, ts in existing.items():
        updated[link] = ts
    for link in all_new_links:
        if link not in updated:
            updated[link] = now_ts
            print(f"New config added: {link[:80]}...")

    # مرتب‌سازی: جدیدترین (بزرگترین timestamp) در ابتدا
    sorted_links = sorted(updated.items(), key=lambda x: x[1], reverse=True)
    new_ordered = OrderedDict()
    for link, ts in sorted_links:
        new_ordered[link] = ts

    # ذخیره دیتابیس
    save_db(new_ordered)
    print(f"Database saved. Total configs: {len(new_ordered)}")

    # مرحله 3: تولید HTML
    last_update_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    links_only = list(new_ordered.keys())
    html_content = generate_html(links_only, last_update_str)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML file '{HTML_FILE}' generated with {len(links_only)} configs.")

if __name__ == "__main__":
    main()
