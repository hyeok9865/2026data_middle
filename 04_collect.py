"""4단계: 선별 URL 본문 수집."""
import json
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()
app = Firecrawl()

TARGETS = [
    # (slug, url, kind)
    ("ko_quasar_deathadder_v4", "https://quasarzone.com/bbs/qc_qsz/views/1975145", "expert_ko"),
    ("ko_quasar_lamzu_maya_x8k", "https://quasarzone.com/bbs/qc_qsz/views/1807673", "expert_ko"),
    ("ko_quasar_superlight2_user", "https://quasarzone.com/bbs/qc_user/views/125174", "user_ko"),
    ("ko_quasar_viper_v3_pro", "https://quasarzone.com/bbs/qc_qsz/views/1726169", "expert_ko"),
    ("ko_blog_vxe_r1_se", "https://blog.naver.com/cristine23/224211148020?viewType=pc", "user_ko"),
    ("ko_blog_zowie_u2", "https://m.blog.naver.com/victoryace89/223652216294", "user_ko"),
    ("ko_blog_deathadder_v4", "https://m.blog.naver.com/skdaksdptn/223988000640", "user_ko"),
    ("ko_nosearch_overview", "https://nosearch.com/recommendation/overview/digitalit/mouse", "expert_ko"),
    ("ko_quasar_mouse_pick", "https://quasarzone.com/bbs/qf_input/views/408436", "user_ko"),
    ("ko_quasar_recommend_thread", "https://quasarzone.com/bbs/qf_input/views/422115", "user_ko"),
    ("en_rtings_sensor_latency", "https://www.rtings.com/mouse/tests/control/sensor-latency", "lab_en"),
    ("en_lttlabs_testing", "https://www.lttlabs.com/articles/2024/12/13/how-labs-conducts-mouse-testing", "lab_en"),
    ("en_reddit_need_new_mouse", "https://www.reddit.com/r/MouseReview/comments/1tw6vwz/", "user_en"),
    ("en_reddit_honest_budget_rank", "https://www.reddit.com/r/MouseReview/comments/1ssdlb7/", "user_en"),
    ("en_reddit_best_moment", "https://www.reddit.com/r/buildapc/comments/1qpyok4/", "user_en"),
    ("en_reddit_dav4_issues", "https://www.reddit.com/r/MouseReview/comments/1r8u0mi/", "user_en"),
    ("en_reddit_zowie_u2", "https://www.reddit.com/r/MouseReview/comments/1b1nx96/", "user_en"),
    ("en_reddit_vaxee_xe_v2", "https://www.reddit.com/r/MouseReview/comments/1rwbn3n/", "user_en"),
    ("en_reddit_sl2_dex", "https://www.reddit.com/r/MouseReview/comments/1n76fx1/", "user_en"),
    ("en_reddit_lamzu_maya_x", "https://www.reddit.com/r/MouseReview/comments/1g4uw14/", "user_en"),
    ("en_reddit_pulsar_x2_cl", "https://www.reddit.com/r/MouseReview/comments/1oy3bh8/", "user_en"),
    ("en_reddit_viper_v3_2mo", "https://www.reddit.com/r/MouseReview/comments/1qbtqao/", "user_en"),
    ("en_reddit_mmo_mouse", "https://www.reddit.com/r/MouseReview/comments/1qwhpp7/", "user_en"),
    ("en_reddit_gaming_mice_lag", "https://www.reddit.com/r/MouseReview/comments/p49dld/", "user_en"),
]

Path("data/raw").mkdir(parents=True, exist_ok=True)
index = []
ok = err = 0

for slug, url, kind in TARGETS:
    md = ""
    used = url
    for candidate in (url, url.rstrip("/") + ".json", "https://old.reddit.com" + url[url.find("/r/"):]):
        try:
            doc = app.scrape(candidate, formats=["markdown"], only_main_content=True, timeout=60000)
            md = getattr(doc, "markdown", "") or ""
            if len(md) > 300:
                used = candidate
                break
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {str(e)[:60]}"
            md = ""

    if len(md) > 300:
        Path(f"data/raw/{slug}.md").write_text(md, encoding="utf-8")
        index.append({"slug": slug, "url": used, "kind": kind, "chars": len(md)})
        print(f"[OK ] {len(md):>7} | {slug}")
        ok += 1
    else:
        print(f"[ERR] {slug}  ({used})")
        err += 1
    time.sleep(0.3)

Path("data/index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n성공 {ok} / 실패 {err}")
