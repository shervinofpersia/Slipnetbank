import re
import requests
import time
from datetime import datetime, timedelta
from collections import OrderedDict

# ========== CONFIGURATION ==========
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

SLIPNET_REGEX = re.compile(r'slipnet(?:-enc)?:\/\/[^\s<>"\'\[\]{}|\\^`]+', re.IGNORECASE)

OUTPUT_FILE = "SlipNet.txt"

# ========== FUNCTIONS ==========
def fetch_channel_page(username: str) -> str:
    """دریافت صفحه عمومی کانال تلگرام"""
    url = f"https://t.me/s/{username}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[!] Error fetching {username}: {e}")
        return ""

def extract_links_from_html(html: str) -> set:
    """استخراج لینک‌های slipnet از HTML (حذف تکراری در همان کانال)"""
    return set(SLIPNET_REGEX.findall(html))

def get_next_refresh(minutes=30) -> str:
    """زمان بعدی به روزرسانی (اکنون + minutes) به فرمت hh:mm AM/PM"""
    now = datetime.now()
    future = now + timedelta(minutes=minutes)
    return future.strftime("%I:%M %p").lstrip("0")

def generate_output(per_channel_data: OrderedDict, total_unique: int) -> str:
    """
    per_channel_data: OrderedDict {channel_name: list_of_unique_links}
    total_unique: تعداد کل لینک‌های یکتا در همه کانال‌ها
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    next_refresh = get_next_refresh(30)

    lines = []
    # Header
    lines.append("☬Exclusive SHΞN™ made")
    lines.append("Live SlipNet Node Collector")
    lines.append(f"Last update: {now_str}      Total node : {total_unique}   Next refresh: {next_refresh}")
    lines.append("")  # خط خالی

    # Sections per channel
    for ch, links in per_channel_data.items():
        count = len(links)
        if count == 0:
            continue
        lines.append(f"Slipnet nod from : {ch} {count} Node")
        for link in links:
            # فقط خود لینک، بدون فاصله اضافه
            lines.append(link)
        lines.append("")  # خط خالی بعد از هر سورس

    # Footer
    lines.append("___________________________")
    lines.append("☬Exclusive SHΞN™ made")
    lines.append("Support: T.me/Shervini")

    return "\n".join(lines)

def main():
    print(f"[{datetime.now().isoformat()}] Starting SlipNet collector (TXT mode)")

    # دیکشنری برای نگهداری لینک‌های هر کانال (حذف تکراری درون هر کانال)
    per_channel_links = OrderedDict()
    all_unique_links = set()  # برای محاسبه کل یکتا (در کل)

    for ch in CHANNELS:
        print(f"  -> Fetching {ch}")
        html = fetch_channel_page(ch)
        if not html:
            per_channel_links[ch] = []
            continue

        links = extract_links_from_html(html)
        if not links:
            per_channel_links[ch] = []
            print(f"      No slipnet links found")
        else:
            # حذف تکراری در همان کانال
            unique_links = list(links)
            per_channel_links[ch] = unique_links
            all_unique_links.update(unique_links)
            print(f"      Found {len(unique_links)} unique slipnet link(s)")

        time.sleep(1)  # احترام به محدودیت

    total_unique_all = len(all_unique_links)
    print(f"Total unique configs (across all channels): {total_unique_all}")

    # تولید محتوای فایل
    output_content = generate_output(per_channel_links, total_unique_all)

    # ذخیره در فایل
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"✅ Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()l
