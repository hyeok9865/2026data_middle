"""11단계(v3): 3개 모델 심층 비교 데이터 -> deck/data.json

인용문은 수집 원문을 직접 확인해 큐레이션하고, 각 항목에 근거 유형을 표기한다.
- 리뷰: 수집된 리뷰 본문에서 확인
- 스펙: 제품 스펙시트/가격
- 데이터: 이번 분석의 집계 결과
"""
import json
import re
from pathlib import Path

import pandas as pd

TARGETS = ["Logitech G PRO X SUPERLIGHT 2", "Razer Viper V3 Pro", "Zowie U2"]
SHORT = {
    "Logitech G PRO X SUPERLIGHT 2": "지슈라2",
    "Razer Viper V3 Pro": "Viper V3 Pro",
    "Zowie U2": "Zowie U2",
}

SPEC = {
    "Logitech G PRO X SUPERLIGHT 2": {
        "weight_g": 60, "sensor": "HERO 2", "max_dpi": 32000,
        "polling_hz": 2000, "polling_note": "DEX 모델은 8,000Hz",
        "switch": "LIGHTFORCE 하이브리드", "battery_h": 95,
        "battery_note": "충전 1회 95시간 (전작 70시간)",
        "software": "G HUB", "price_krw": [180000, 220000], "price_label": "18~22만원",
        "shape": "대칭형 · 미들",
    },
    "Razer Viper V3 Pro": {
        "weight_g": 54, "sensor": "Focus Pro 35K (2세대)", "max_dpi": 35000,
        "polling_hz": 8000, "polling_note": "무선 8,000Hz / 유선 1,000Hz",
        "switch": "3세대 옵티컬", "battery_h": None,
        "battery_note": "공식 배터리 수치 미확인",
        "software": "Razer Synapse", "price_krw": [179000, 239000], "price_label": "17.9~23.9만원",
        "shape": "대칭형 · 로우",
    },
    "Zowie U2": {
        "weight_g": 60, "sensor": "PixArt PAW3950", "max_dpi": 32000,
        "polling_hz": 4000, "polling_note": "U2-DW 기준 · 기본 U2는 1,000Hz",
        "switch": "기계식", "battery_h": 80,
        "battery_note": "80h@1kHz / 30h@2kHz / 24h@4kHz",
        "software": "불필요 (본체 버튼)", "price_krw": [251500, 276650], "price_label": "약 25~27만원",
        "shape": "대칭형 · 미들 (FPS)",
    },
}

# 수집 원문 + 스펙을 근거로 정리한 장단점
CURATED = {
    "Logitech G PRO X SUPERLIGHT 2": {
        "pros": [
            ("60g + HERO 2(500 IPS·40G). 2세대에서 무게 63→60g, 배터리 70→95시간으로 개선", "스펙"),
            ("LIGHTFORCE 하이브리드 스위치 — 기계식 클릭감을 유지하면서 더블클릭 이슈 완화", "리뷰"),
            ("“쫀득함과 탄탄함을 동시에 느낄 수 있는 클릭감” — 수집 리뷰 다수", "리뷰"),
            ("언급 80건·소스 12개로 3종 중 압도적. A/S·중고 수요가 가장 두터움", "데이터"),
        ],
        "cons": [
            ("18~22만원 — 3종 중 최상위 가격대", "스펙"),
            ("기본 폴링은 2,000Hz. 8,000Hz는 DEX 모델에서만 지원", "스펙"),
            ("DEX 모델은 오른손 비대칭 — 왼손 사용자에게 불편", "리뷰"),
            ("광축 전환 후 “소리가 커지고 딱딱해졌다”는 사용자 지적", "리뷰"),
        ],
    },
    "Razer Viper V3 Pro": {
        "pros": [
            ("54g — 3종 중 최경량", "스펙"),
            ("무선 8,000Hz 폴링. 유선 연결 시 1,000Hz", "스펙"),
            ("3세대 옵티컬 스위치 — “기계식보다 소음이 작고 균일해졌다”", "리뷰"),
            ("Focus Pro 35K, DPI 1단위 조절 + 감도 매처로 감도 이식이 쉬움", "리뷰"),
        ],
        "cons": [
            ("8,000Hz는 “정상 활용 조건”이 별도로 필요 — 체감 논란이 있음", "리뷰"),
            ("17.9~23.9만원 — 지슈라2와 함께 최상위 가격대", "스펙"),
            ("부정 인용문 비율이 3종 중 가장 낮음 → 약점 정보 자체가 부족", "데이터"),
            ("공식 배터리 수치가 확인되지 않음", "스펙"),
        ],
    },
    "Zowie U2": {
        "pros": [
            ("본체 버튼으로 DPI·폴링·LOD 조절 — 소프트웨어 설치가 필요 없음", "리뷰"),
            ("60g + PAW3950. “가볍지만 날림이 적어 정교한 브레이킹이 가능”", "리뷰"),
            ("4,000Hz + 스탠드형 리시버(충전 독 겸용)", "스펙"),
            ("FPS 클로그립 최적화 — e스포츠 지향 설계", "리뷰"),
        ],
        "cons": [
            ("약 25~27만원 — 3종 중 최고가", "스펙"),
            ("4,000Hz에서 배터리 24시간. 1,000Hz(80시간) 대비 1/3 수준", "스펙"),
            ("매크로·프로파일 등 소프트웨어 기능이 없음 — 호불호", "스펙"),
            ("만족도 100%는 표본 4개 소스의 착시. 부정 후기 자체가 수집되지 않음", "데이터"),
        ],
    },
}

POS_KW = ["좋", "만족", "추천", "최고", "훌륭", "편하", "가볍", "정확", "안정", "괜찮", "완벽",
          "부드럽", "빠르", "뛰어", "우수", "매력", "강력", "준수", "무난", "편리", "쾌적"]
NEG_KW = ["아쉽", "아쉬", "단점", "별로", "실망", "비싸", "비쌈", "무겁", "불량", "불편", "문제",
          "지연", "소음", "더블클릭", "씹힘", "끊김", "복불복", "유격", "고장", "부족", "피로", "논란"]
NOISE = ["youtube", "tap to unmute", "watch on", "subscribers", "q station", "http", ".com", ".co.kr",
         "네이버 블로그", "구독", "댓글", "저작권", "무단", "재배포", "광고", "제휴", "쿠팡",
         "파트너스", "본문", "카테고리", "이웃추가", "바로가기", "판매처", "지연 시간 테스트"]


def clean(s: str) -> str:
    s = re.sub(r"<[^<>]{0,60}>?", " ", s)
    s = s.replace("\u200b", " ").replace("\\", " ")
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def usable(s: str) -> bool:
    low = s.lower()
    return (30 <= len(s) <= 320
            and not any(n in low for n in NOISE)
            and len(re.findall(r"[가-힣]", s)) >= 18)


summ = pd.read_csv("data/summary.csv").set_index("model")
ment = pd.read_csv("data/mentions.csv")
ment = ment[ment.model.isin(TARGETS)]

models = []
for m in TARGETS:
    s = summ.loc[m]
    sub = ment[ment.model == m]
    spec = SPEC[m]

    rows = []
    for txt in sub.sentence.astype(str):
        t = clean(txt)
        if not usable(t):
            continue
        if m == "Logitech G PRO X SUPERLIGHT 2" and "dex" in t.lower():
            continue
        low = t.lower()
        rows.append({
            "pos": sum(low.count(k) for k in POS_KW),
            "neg": sum(low.count(k) for k in NEG_KW),
        })

    neg_ratio = round(sum(1 for r in rows if r["neg"] > 0) / max(len(rows), 1) * 100, 1)
    cur = CURATED[m]
    w = spec["weight_g"]
    price_mid = sum(spec["price_krw"]) / 2

    models.append({
        "key": m, "name": SHORT[m], "full": m, "brand": s.brand,
        "metrics": {
            "mentions": int(s.mentions),
            "opinion": int(s.opinion_mentions),
            "sources": int(s.sources),
            "satisfaction": None if pd.isna(s.satisfaction) else float(s.satisfaction),
            "attention": float(s.attention),
            "coverage": float(s.coverage),
            "score": None if pd.isna(s.score) else float(s.score),
            "neg_ratio": neg_ratio,
            "quotes": len(rows),
        },
        "spec": spec,
        "radar": [
            float(s.satisfaction) if not pd.isna(s.satisfaction) else 50.0,
            float(s.attention),
            min(100.0, float(s.coverage) * 3),
            round(max(0.0, 100 - (w - 45) * 4), 1),
            round(max(0.0, 100 - (price_mid - 170000) / 1200), 1),
        ],
        "pros": [{"t": t, "basis": b} for t, b in cur["pros"]],
        "cons": [{"t": t, "basis": b} for t, b in cur["cons"]],
        "keywords": {
            "pos": int(sum(r["pos"] for r in rows)),
            "neg": int(sum(r["neg"] for r in rows)),
        },
    })

data = {
    "generated": "2026-10-30",
    "models": models,
    "radar_axes": ["만족도", "인기도", "근거량", "경량성", "가격접근성"],
    "comparison_rows": [
        {"label": "무게", "values": [f"{m['spec']['weight_g']}g" for m in models], "best": "min"},
        {"label": "센서", "values": [m["spec"]["sensor"] for m in models], "best": None},
        {"label": "최대 DPI", "values": [f"{m['spec']['max_dpi']:,}" for m in models], "best": "max"},
        {"label": "폴링레이트", "values": [f"{m['spec']['polling_hz']:,}Hz" for m in models], "best": "max"},
        {"label": "스위치", "values": [m["spec"]["switch"] for m in models], "best": None},
        {"label": "배터리", "values": [f"{m['spec']['battery_h']}시간" if m["spec"]["battery_h"] else "미확인" for m in models], "best": "max"},
        {"label": "소프트웨어", "values": [m["spec"]["software"] for m in models], "best": None},
        {"label": "형태", "values": [m["spec"]["shape"] for m in models], "best": None},
        {"label": "국내가", "values": [m["spec"]["price_label"] for m in models], "best": "min"},
    ],
    "battery_notes": [m["spec"]["battery_note"] for m in models],
    "polling_notes": [m["spec"]["polling_note"] for m in models],
    "totals": {"sources": 38, "sentences": 2685, "matches": 420, "chars": 900000},
}

Path("deck").mkdir(exist_ok=True)
Path("deck/data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

for m in models:
    print("=" * 62)
    print(f"{m['name']} — 인용 {m['metrics']['quotes']}건 / 부정문 {m['metrics']['neg_ratio']}% / 긍정어 {m['keywords']['pos']}·부정어 {m['keywords']['neg']}")
    for p in m["pros"]:
        print(f"  + [{p['basis']}] {p['t']}")
    for c in m["cons"]:
        print(f"  - [{c['basis']}] {c['t']}")
