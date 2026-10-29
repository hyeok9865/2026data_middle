"""9단계: 장점/단점/가격/스펙 추출."""
import json
import re
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
df = pd.read_csv("data/mentions.csv")

CONS_KW = ["단점", "아쉬", "문제", "불량", "이슈", "논란", "더블클릭", "씹힘", "끊김", "지연", "무겁",
           "비싸", "실망", "후회", "환불", "반품", "QC", "복불복", "유격", "휘", "흔들", "마모", "불편",
           "부족", "피로", "소음", "발열", "별로", "최악", "덜컥", "뻑뻑", "아깝", "아쉽"]
PROS_KW = ["좋", "만족", "추천", "최고", "훌륭", "뛰어", "편하", "가볍", "정확", "안정", "괜찮", "완벽",
           "깔끔", "고급", "탄탄", "부드럽", "빠르", "우수", "매력", "강력", "가성비", "대만족", "맘에"]

PRICE_RE = re.compile(r"(\d{1,3}(?:,\d{3})+|\d+)\s*원|(\d+(?:\.\d+)?)\s*~?\s*(\d+(?:\.\d+)?)?\s*만\s*원")
WEIGHT_RE = re.compile(r"(\d{2,3}(?:\.\d)?)\s*(?:g|그램)")

lines = []
price_rows = []

for model, sub in df.groupby("model"):
    n = len(sub)
    pros = sub[sub.sentence.str.contains("|".join(PROS_KW), case=False, na=False) & (sub.pos > sub.neg)]
    cons = sub[sub.sentence.str.contains("|".join(CONS_KW), case=False, na=False)]
    lines.append(f"\n\n{'#'*3} {model}  (언급 {n} / 긍정문 {len(pros)} / 부정키워드문 {len(cons)})")

    lines.append("  [장점 근거]")
    seen = set()
    for s in pros.drop_duplicates("sentence").sentence:
        k = re.sub(r"\W", "", s)[:60]
        if k in seen:
            continue
        seen.add(k)
        lines.append(f"    + {s[:260]}")
        if len(seen) >= 6:
            break

    lines.append("  [단점/문제 근거]")
    seen = set()
    for s in cons.drop_duplicates("sentence").sentence:
        k = re.sub(r"\W", "", s)[:60]
        if k in seen:
            continue
        seen.add(k)
        lines.append(f"    - {s[:260]}")
        if len(seen) >= 6:
            break

# 가격/무게: 원문 전체에서 모델명 근처 문장 스캔
import importlib.util
spec = importlib.util.spec_from_file_location("an", "06_analyze.py")
# 모델 별칭 재사용을 위해 직접 로드하지 않고 간단 매핑 사용
ALIAS_SEARCH = {
    "Logitech G PRO X SUPERLIGHT 2 DEX": ["superlight 2 dex", "지슈라2 dex", "지슈라 2 덱스"],
    "Logitech G PRO X SUPERLIGHT 2": ["superlight 2", "지슈라2", "지슈라 2"],
    "Logitech G PRO X SUPERLIGHT": ["superlight", "지슈라"],
    "Logitech G304 / G305": ["g304", "g305"],
    "Logitech G102 / G203": ["g102", "g203"],
    "Logitech G502 X": ["g502"],
    "Razer Viper V3 Pro": ["viper v3", "바이퍼 v3"],
    "Razer Viper V4 Pro": ["viper v4", "바이퍼 v4"],
    "Razer DeathAdder V4 Pro": ["deathadder v4", "데스에더 v4"],
    "Razer DeathAdder V3 Pro": ["deathadder v3", "데스에더 v3"],
    "Razer Basilisk V3 Pro": ["basilisk", "바실리스크"],
    "Zowie U2": ["조위 u2", "zowie u2"],
    "VAXEE XE / XE V2": ["vaxee"],
    "Lamzu Maya X": ["maya x", "마야 x"],
    "Pulsar X2 / X2V2": ["펄사 x2", "pulsar x2"],
    "ATK / VXE (잠자리)": ["vxe r1", "atk", "잠자리 마우스"],
    "Ninjutso Sora": ["sora", "소라"],
}

raw_texts = []
for f in RAW.glob("*.md"):
    if re.match(r"^\d\d_", f.stem):
        continue
    raw_texts.append((f.stem, f.read_text(encoding="utf-8", errors="ignore")))

for model, aliases in ALIAS_SEARCH.items():
    prices, weights = [], []
    for stem, txt in raw_texts:
        for sent in re.split(r"[\n.。!?]", txt):
            low = sent.lower()
            if not any(a in low for a in aliases):
                continue
            if len(sent) > 300 or "원" not in sent and "만" not in sent:
                pass
            for m in PRICE_RE.finditer(sent):
                s = m.group(0)
                if "만" in s:
                    a = float(m.group(2)); b = m.group(3)
                    v = (a + float(b)) / 2 * 10000 if b else a * 10000
                else:
                    v = float(m.group(1).replace(",", ""))
                if 10000 <= v <= 900000:
                    prices.append(int(v))
            for m in WEIGHT_RE.finditer(sent):
                w = float(m.group(1))
                if 35 <= w <= 150:
                    weights.append(w)
    if prices or weights:
        price_rows.append({
            "model": model,
            "price_n": len(prices),
            "price_min": min(prices) if prices else None,
            "price_max": max(prices) if prices else None,
            "price_median": int(pd.Series(prices).median()) if prices else None,
            "weight_median_g": round(float(pd.Series(weights).median()), 1) if weights else None,
        })

pd.DataFrame(price_rows).to_csv("data/price_spec.csv", index=False, encoding="utf-8-sig")
Path("data/pros_cons.txt").write_text("\n".join(lines), encoding="utf-8")
print(pd.DataFrame(price_rows).to_string(index=False))
print("\n-> data/pros_cons.txt, data/price_spec.csv")
