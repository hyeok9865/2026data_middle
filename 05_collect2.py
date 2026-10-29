"""5단계: 추가 소스 수집 (레이트리밋 준수)."""
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()
app = Firecrawl()

TARGETS = [
    ("ko_blog_gaming_mouse_2026_top7", "https://m.blog.naver.com/da_young1480/224283410772", "expert_ko"),
    ("ko_blog_gaming_mouse_2025", "https://m.blog.naver.com/forbetteritlife22/223828981065", "expert_ko"),
    ("ko_blog_sl2_jihoon", "https://blog.naver.com/jihoon5252/223440790544?viewType=pc", "user_ko"),
    ("ko_blog_viper_v3_2mo", "https://blog.naver.com/oksk2002kr/223505036623", "user_ko"),
    ("ko_blog_sl2_dex_heading", "https://m.blog.naver.com/heading100/223951400649", "user_ko"),
    ("ko_blog_sl2_dex_anisaver", "https://blog.naver.com/anisaver/223621243839", "user_ko"),
    ("ko_tistory_sl2_dex", "https://tambo.tistory.com/31", "user_ko"),
    ("ko_tistory_sl2_compare", "https://swchoo6087.tistory.com/343", "user_ko"),
    ("ko_danawa_pulsar_x2", "https://prod.danawa.com/info/?pcode=17679110", "price_ko"),
    ("en_rtings_wireless_gaming", "https://www.rtings.com/mouse/reviews/best/wireless-gaming", "lab_en"),
    ("en_pcmag_gaming_mice", "https://www.pcmag.com/picks/the-best-gaming-mice", "expert_en"),
    ("en_techradar_gaming_mouse", "https://www.techradar.com/news/best-gaming-mouse", "expert_en"),
]

Path("data/raw").mkdir(parents=True, exist_ok=True)
index = Path("data/index.json")
existing = json.loads(index.read_text(encoding="utf-8")) if index.exists() else []
have = {r["slug"] for r in existing}

ok = err = 0
for slug, url, kind in TARGETS:
    if slug in have:
        print(f"[SKIP] {slug}")
        continue
    md = ""
    for attempt in range(3):
        try:
            doc = app.scrape(url, formats=["markdown"], only_main_content=True, timeout=90000)
            md = getattr(doc, "markdown", "") or ""
            break
        except Exception as e:  # noqa: BLE001
            msg = str(e)[:80]
            if "Rate Limit" in msg or "RateLimit" in type(e).__name__:
                time.sleep(35)
                continue
            print(f"[ERR] {slug}: {type(e).__name__}: {msg}")
            break

    if len(md) > 500:
        Path(f"data/raw/{slug}.md").write_text(md, encoding="utf-8")
        existing.append({"slug": slug, "url": url, "kind": kind, "chars": len(md)})
        print(f"[OK ] {len(md):>7} | {slug}")
        ok += 1
    else:
        if len(md) <= 500:
            print(f"[MISS] {slug} ({len(md)} chars)")
        err += 1
    time.sleep(3.5)

index.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n성공 {ok} / 실패 {err} / 누적 {len(existing)}")
