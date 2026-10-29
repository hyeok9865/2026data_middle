"""1단계: 리뷰 소스 탐색 (Firecrawl search)."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()
app = Firecrawl()

QUERIES = [
    "게이밍 마우스 추천 리뷰 2026",
    "무선 게이밍 마우스 비교 리뷰",
    "gaming mouse review 2026 best",
    "로지텍 G Pro X Superlight 2 리뷰",
    "Razer Viper V3 Pro 리뷰",
]

out = []
for q in QUERIES:
    try:
        res = app.search(q, limit=6)
        items = res.web or []
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {q}: {type(e).__name__}: {e}")
        continue

    print(f"\n=== {q}  ({len(items)}) ===")
    for it in items:
        rec = {
            "query": q,
            "title": getattr(it, "title", None),
            "url": getattr(it, "url", None),
            "description": getattr(it, "description", None),
        }
        out.append(rec)
        print(f"- {rec['title']}\n  {rec['url']}")

Path("data").mkdir(exist_ok=True)
with open("data/search_results.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"\n총 {len(out)}건 저장 -> data/search_results.json")
