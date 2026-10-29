"""2단계: 소스별 스크래핑 가능 여부 확인."""
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()
app = Firecrawl()

URLS = [
    "https://www.rtings.com/mouse/reviews/best/by-usage/gaming",
    "https://www.tomshardware.com/best-picks/best-gaming-mouse",
    "https://quasarzone.com/bbs/qf_input/views/408436",
    "https://nosearch.com/recommendation/pick/digitalit/mouse/%EA%B2%8C%EC%9D%B4%EB%B0%8D",
    "https://prod.danawa.com/list/?cate=11310719",
]

Path("data/raw").mkdir(parents=True, exist_ok=True)

for i, url in enumerate(URLS, 1):
    try:
        doc = app.scrape(url, formats=["markdown"], only_main_content=True, timeout=60000)
        md = getattr(doc, "markdown", "") or ""
        name = re.sub(r"[^a-zA-Z0-9]+", "_", url.split("//")[1])[:60]
        Path(f"data/raw/{i:02d}_{name}.md").write_text(md, encoding="utf-8")
        print(f"[OK ] {len(md):>7} chars | {url}")
        print(f"     head: {md[:120].replace(chr(10), ' ')}")
    except Exception as e:  # noqa: BLE001
        print(f"[ERR] {type(e).__name__}: {str(e)[:150]} | {url}")
