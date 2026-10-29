"""7단계: 핵심 모델 사용후기 집중 수집."""
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()
app = Firecrawl()

QUERIES = [
    "지슈라2 단점 후기 6개월 사용",
    "로지텍 G304 장단점 후기",
    "레이저 바이퍼 V3 프로 단점 후기",
    "데스에더 V4 프로 단점 아쉬운점",
    "VXE R1 SE+ 단점 후기",
    "람주 마야 X 단점 후기",
    "펄사 X2 후기 장단점",
    "조위 U2 단점 후기",
    "닌저소 소라 V2 후기",
    "게이밍 마우스 무게 지연 비교 측정",
]

cands = []
for q in QUERIES:
    for attempt in range(3):
        try:
            res = app.search(q, limit=5)
            items = res.web or []
            break
        except Exception as e:  # noqa: BLE001
            if "Rate" in str(e) or "RateLimit" in type(e).__name__:
                time.sleep(35)
                continue
            print(f"[FAIL] {q}: {str(e)[:60]}")
            items = []
            break
    print(f"\n=== {q} ({len(items)})")
    for it in items:
        u = getattr(it, "url", "") or ""
        if any(b in u for b in ("youtube.com", "instagram.com", "tiktok.com", "reddit.com", "dcinside.com")):
            continue
        cands.append({"query": q, "url": u, "title": getattr(it, "title", None)})
        print(f"  + {u}")
    time.sleep(2)

Path("data/search_results_round3.json").write_text(
    json.dumps(cands, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"\n수집 후보 {len(cands)}건")
