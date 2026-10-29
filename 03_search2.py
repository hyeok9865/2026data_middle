"""3단계: 모델별/커뮤니티 리뷰 추가 검색."""
import json
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()
app = Firecrawl()

QUERIES = [
    "레이저 데스에더 V4 프로 리뷰",
    "로지텍 G Pro X Superlight 2 DEX 리뷰",
    "조위 Zowie U2 리뷰 후기",
    "VAXEE 무선 마우스 리뷰",
    "람주 Lamzu Maya X 리뷰",
    "Pulsar X2 무선 마우스 리뷰",
    "잠자리 마우스 공격수 리뷰 가성비",
    "퀘이사존 게이밍 마우스 사용기",
    "reddit MouseReview best mouse 2026 recommendations",
    "gaming mouse latency sensor weight comparison test",
]

out = []
for q in QUERIES:
    try:
        res = app.search(q, limit=5)
        items = res.web or []
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] {q}: {type(e).__name__}: {str(e)[:80]}")
        continue
    print(f"\n=== {q} ({len(items)}) ===")
    for it in items:
        rec = {
            "query": q,
            "title": getattr(it, "title", None),
            "url": getattr(it, "url", None),
            "description": getattr(it, "description", None),
        }
        out.append(rec)
        print(f"- {rec['title'][:70] if rec['title'] else ''}\n  {rec['url']}")

Path("data").mkdir(exist_ok=True)
p = Path("data/search_results_round2.json")
p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n총 {len(out)}건 -> {p}")
