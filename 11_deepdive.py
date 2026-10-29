"""11단계: 3개 모델 심층 비교 데이터 생성 -> deck/data.json"""
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

# 수집 원문에서 검증한 스펙 (출처: 퀘이사존 사용기 / 네이버 블로그 / 노써치)
SPEC = {
    "Logitech G PRO X SUPERLIGHT 2": {
        "weight_g": 60,
        "sensor": "HERO 2",
        "max_dpi": 32000,
        "ips": 500,
        "accel_g": 40,
        "polling_hz": 2000,
        "polling_note": "DEX 모델 8,000Hz",
        "switch": "LIGHTFORCE 하이브리드",
        "battery_h": 95,
        "software": "G HUB",
        "price_krw": [180000, 220000],
        "price_label": "18~22만원",
        "shape": "대칭형 · 미들",
    },
    "Razer Viper V3 Pro": {
        "weight_g": 54,
        "sensor": "Focus Pro 35K (2세대)",
        "max_dpi": 35000,
        "ips": None,
        "accel_g": None,
        "polling_hz": 8000,
        "polling_note": "무선 8,000Hz / 유선 1,000Hz",
        "switch": "3세대 옵티컬",
        "battery_h": None,
        "software": "Razer Synapse",
        "price_krw": [179000, 239000],
        "price_label": "17.9~23.9만원",
        "shape": "대칭형 · 로우",
    },
    "Zowie U2": {
        "weight_g": 60,
        "sensor": "PixArt PAW3950",
        "max_dpi": 32000,
        "ips": None,
        "accel_g": None,
        "polling_hz": 4000,
        "polling_note": "U2-DW 기준. 기본 U2는 1,000Hz",
        "switch": "기계식",
        "battery_h": 80,
        "software": "불필요 (본체 버튼)",
        "price_krw": [251500, 276650],
        "price_label": "약 25~27만원",
        "shape": "대칭형 · 미들 (FPS)",
    },
}

summ = pd.read_csv("data/summary.csv").set_index("model")
ment = pd.read_csv("data/mentions.csv")
ment = ment[ment.model.isin(TARGETS)]

POS_KW = ["좋", "만족", "추천", "최고", "훌륭", "편하", "가볍", "정확", "안정", "괜찮", "완벽", "부드럽", "빠르"]
NEG_KW = ["아쉽", "단점", "비싸", "무겁", "불편", "문제", "지연", "소음", "더블클릭", "불량", "실망"]

models = []
for m in TARGETS:
    s = summ.loc[m]
    sub = ment[ment.model == m]
    neg = sub[sub.neg > sub.pos]
    spec = SPEC[m]
    w = spec["weight_g"]
    price_mid = sum(spec["price_krw"]) / 2
    models.append({
        "key": m,
        "name": SHORT[m],
        "full": m,
        "brand": s.brand,
        "metrics": {
            "mentions": int(s.mentions),
            "opinion": int(s.opinion_mentions),
            "sources": int(s.sources),
            "satisfaction": None if pd.isna(s.satisfaction) else float(s.satisfaction),
            "attention": float(s.attention),
            "coverage": float(s.coverage),
            "score": None if pd.isna(s.score) else float(s.score),
            "neg_ratio": round(len(neg) / max(len(sub), 1) * 100, 1),
        },
        "spec": spec,
        # 레이더: 만족도 / 인기도 / 근거량 / 경량성 / 가격접근성
        "radar": [
            float(s.satisfaction) if not pd.isna(s.satisfaction) else 50.0,
            float(s.attention),
            min(100.0, float(s.coverage) * 3),
            round(max(0.0, 100 - (w - 45) * 4), 1),
            round(max(0.0, 100 - (price_mid - 170000) / 1200), 1),
        ],
        "pros": list(dict.fromkeys(
            x[:150] for x in sub[(sub.pos > sub.neg) & sub.sentence.str.contains("|".join(POS_KW), na=False)].sentence
        ))[:3],
        "cons": list(dict.fromkeys(x[:150] for x in neg.sentence))[:3],
        "keywords": {
            "pos": int(sum(sub.sentence.str.count(k).sum() for k in POS_KW)),
            "neg": int(sum(sub.sentence.str.count(k).sum() for k in NEG_KW)),
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
    "totals": {
        "sources": 38,
        "sentences": 2685,
        "matches": 420,
        "chars": 900000,
    },
}

Path("deck").mkdir(exist_ok=True)
Path("deck/data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

rows = []
for m in models:
    rows.append({
        "모델": m["name"], "무게(g)": m["spec"]["weight_g"], "폴링(Hz)": m["spec"]["polling_hz"],
        "언급": m["metrics"]["mentions"], "의견": m["metrics"]["opinion"],
        "만족도": m["metrics"]["satisfaction"], "소스": m["metrics"]["sources"],
        "점수": m["metrics"]["score"], "부정비율(%)": m["metrics"]["neg_ratio"],
    })
pd.DataFrame(rows).to_csv("data/deepdive.csv", index=False, encoding="utf-8-sig")

print(json.dumps(data["models"][0]["metrics"], ensure_ascii=False))
print("-> deck/data.json, data/deepdive.csv")
