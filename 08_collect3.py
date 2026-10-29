"""8단계: 후보 본문 수집."""
import json
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()
app = Firecrawl()

cands = json.loads(Path("data/search_results_round3.json").read_text(encoding="utf-8"))
IDX = Path("data/index.json")
index = json.loads(IDX.read_text(encoding="utf-8")) if IDX.exists() else []
have_urls = {r["url"].rstrip("/") for r in index}

MODEL_SLUG = [
    ("superlight 2", "지슈라2"), ("g304", "g304"), ("g305", "g304"),
    ("viper", "viperv3"), ("바이퍼", "viperv3"), ("deathadder", "dav4"), ("데스에더", "dav4"),
    ("vxe", "vxe"), ("maya", "mayax"), ("마야", "mayax"),
    ("pulsar", "pulsar"), ("펄사", "pulsar"), ("zowie", "u2"), ("조위", "u2"),
    ("sora", "sora"), ("소라", "sora"),
]

ok = err = 0
for c in cands:
    url = c["url"]
    if url.rstrip("/") in have_urls:
        print(f"[SKIP] {url[:70]}")
        continue
    m = next((s for k, s in MODEL_SLUG if k in url.lower()), None)
    if m is None:
        m = next((s for k, s in MODEL_SLUG if k in (c.get("title") or "").lower()), "etc")

    slug = f"r3_{m}_{re.sub(r'[^a-z0-9]', '', url.split('//')[1].split('/')[0])[:14]}_{ok}"
    md = ""
    for attempt in range(3):
        try:
            doc = app.scrape(url, formats=["markdown"], only_main_content=True, timeout=90000)
            md = getattr(doc, "markdown", "") or ""
            break
        except Exception as e:  # noqa: BLE001
            if "Rate" in str(e) or "RateLimit" in type(e).__name__:
                time.sleep(35)
                continue
            print(f"[ERR] {slug}: {type(e).__name__}: {str(e)[:70]}")
            break

    if len(md) > 800:
        Path(f"data/raw/{slug}.md").write_text(md, encoding="utf-8")
        index.append({"slug": slug, "url": url, "kind": "user_ko", "chars": len(md)})
        have_urls.add(url.rstrip("/"))
        print(f"[OK ] {len(md):>7} | {slug}")
        ok += 1
    else:
        err += 1
    time.sleep(3.2)

IDX.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n성공 {ok} / 실패 {err} / 총 소스 {len(index)}")
