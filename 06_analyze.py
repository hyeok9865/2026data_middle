"""6단계(개선): 노이즈 제거 + 부정어 처리 감성 분석."""
import json
import math
import re
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
IDX = Path("data/index.json")

MODELS = [
    ("Logitech G PRO X SUPERLIGHT 2 DEX", "Logitech", "플래그십", ["superlight 2 dex", "슈퍼라이트 2 dex", "지슈라2 dex", "지슈라 2 dex", "gpx2 dex"]),
    ("Logitech G PRO X SUPERLIGHT 2", "Logitech", "플래그십", ["superlight 2", "슈퍼라이트 2", "지슈라2", "지슈라 2", "gpx2", "g pro x superlight 2"]),
    ("Logitech G PRO X SUPERLIGHT", "Logitech", "플래그십", ["superlight", "슈퍼라이트", "지슈라"]),
    ("Logitech G PRO 2 / SUPERSTRIKE", "Logitech", "플래그십", ["superstrike", "pro 2 lightspeed"]),
    ("Logitech G502 X", "Logitech", "중급", ["g502 x", "g502x", "g502"]),
    ("Logitech G309", "Logitech", "중급", ["g309"]),
    ("Logitech G304 / G305", "Logitech", "보급", ["g304", "g305"]),
    ("Logitech G102 / G203", "Logitech", "보급", ["g102", "g203"]),
    ("Razer Viper V4 Pro", "Razer", "플래그십", ["viper v4 pro", "바이퍼 v4 프로"]),
    ("Razer Viper V3 Pro", "Razer", "플래그십", ["viper v3 pro", "바이퍼 v3 프로", "viper v3"]),
    ("Razer DeathAdder V4 Pro", "Razer", "플래그십", ["deathadder v4 pro", "데스에더 v4 프로", "dav4"]),
    ("Razer DeathAdder V3 Pro", "Razer", "플래그십", ["deathadder v3 pro", "데스에더 v3 프로"]),
    ("Razer Basilisk V3 Pro", "Razer", "중급", ["basilisk", "바실리스크"]),
    ("Zowie U2", "Zowie", "플래그십", ["zowie u2", "조위 u2"]),
    ("Zowie EC2-CW", "Zowie", "플래그십", ["ec2-cw", "ec2 cw", "ec2cw"]),
    ("VAXEE XE / XE V2", "VAXEE", "플래그십", ["vaxee xe", "vaxee"]),
    ("Lamzu Maya X", "Lamzu", "중급", ["maya x", "마야 x", "마야x", "lamzu maya"]),
    ("Pulsar X2 / X2V2", "Pulsar", "중급", ["pulsar x2", "펄사 x2", "x2 crazylight", "x2v2"]),
    ("Ninjutso Sora", "Ninjutso", "중급", ["ninjutso", "sora v2"]),
    ("ATK / VXE (잠자리)", "ATK", "보급", ["vxe r1", "atk vxe", "잠자리 마우스", "r1 se", "r1 pro"]),
    ("Endgame Gear OP1", "Endgame", "중급", ["op1 8k", "endgame gear", "엔드게임"]),
    ("Corsair Sabre V3 Pro", "Corsair", "플래그십", ["sabre v3", "세이버 v3"]),
    ("SteelSeries Aerox", "SteelSeries", "중급", ["aerox", "에어록스"]),
]

ALIASES = sorted(((a.lower(), n, b, s) for n, b, s, al in MODELS for a in al), key=lambda x: -len(x[0]))
MODEL_META = {n: (b, s) for n, b, s, _ in MODELS}

POS = ["좋", "만족", "추천", "최고", "훌륭", "뛰어", "편하", "가볍", "정확", "안정", "괜찮", "완벽", "깔끔", "고급",
       "탄탄", "부드럽", "빠르", "우수", "호평", "합격", "매력", "강력", "준수", "무난", "역대급", "혁신", "가성비",
       "대만족", "맘에", "마음에", "튼튼", "든든", "신뢰", "쾌적", "경쾌", "찰지", "익숙", "적응", "훌륭하", "감동",
       "편리", "안정적", "정갈", "고급스", "세련", "쓸만", "만족스", "뛰어나", "최상", "베스트", "추천드"]
NEG = ["아쉽", "아쉬", "단점", "별로", "실망", "비싸", "비쌈", "무겁", "불량", "불편", "문제", "이슈", "논란",
       "더블클릭", "씹힘", "끊김", "지연", "발열", "소음", "약하", "부실", "최악", "후회", "환불", "반품", "구리",
       "부족", "애매", "복불복", "유격", "덜컹", "고장", "먹통", "안됨", "못쓰", "휘청", "흔들", "삐걱", "뻑뻑",
       "헐거", "떨어짐", "마모", "피로", "시끄", "찝찝", "아깝", "실패", "폄하"]
EN_POS = ["great", "excellent", "best", "love", "solid", "comfortable", "lightweight", "accurate", "recommend",
          "impressive", "perfect", "smooth", "premium", "worth", "amazing", "fantastic", "outstanding", "superb",
          "stellar", "flawless", "bang for", "budget-friendly", "top pick", "standout"]
EN_NEG = ["bad", "poor", "disappoint", "expensive", "heavy", "issue", "problem", "double click", "double-click",
          "creaky", "flex", "rattle", "defect", "quality control", "return", "refund", "worse", "meh",
          "overpriced", "flaw", "mushy", "wobble", "wears", "peeling"]

NEGATORS = ["않", "없", "안 ", "지 않", "않았", "않음", "않고", "아니", "못 "]
BOILER = ["쿠키", "로그인", "회원가입", "댓글", "구독", "공유", "바로가기", "본문으로", "이전글", "다음글",
          "저작권", "무단전재", "재배포", "광고", "제휴", "http", "ad.", "copyright", "all rights"]


def score_text(t: str) -> tuple[int, int]:
    low = t.lower()
    p = n = 0
    for w in POS:
        for m in re.finditer(re.escape(w), low):
            tail = low[m.end(): m.end() + 12]
            if any(ng in tail for ng in NEGATORS):
                n += 1
            else:
                p += 1
    for w in EN_POS:
        p += low.count(w)
    for w in NEG:
        for m in re.finditer(re.escape(w), low):
            tail = low[m.end(): m.end() + 12]
            if any(ng in tail for ng in NEGATORS):
                p += 1
            else:
                n += 1
    for w in EN_NEG:
        n += low.count(w)
    return p, n


def strip_md(t: str) -> str:
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[#*>`|]+", " ", t)
    t = re.sub(r"\\{2,}", " ", t)
    t = re.sub(r"[ \t]+", " ", t)
    return t


def split_sentences(t: str) -> list[str]:
    parts = re.split(r"(?<=[.!?。])\s+|\n{2,}|\n\s*[-*]\s+", t)
    out = []
    for p in parts:
        p = p.strip()
        if not (30 <= len(p) <= 400):
            continue
        if any(b in p.lower() for b in BOILER):
            continue
        out.append(p)
    return out


kind_of = {}
if IDX.exists():
    for r in json.loads(IDX.read_text(encoding="utf-8")):
        kind_of[r["slug"]] = r["kind"]

records, source_stats = [], []

for f in sorted(RAW.glob("*.md")):
    if re.match(r"^\d\d_", f.stem):
        continue
    kind = kind_of.get(f.stem, "user_ko")
    if kind == "price_ko":
        continue  # 가격 페이지는 감성분석 제외
    text = strip_md(f.read_text(encoding="utf-8", errors="ignore"))
    sents = split_sentences(text)
    source_stats.append({"source": f.stem, "kind": kind, "chars": len(text), "sentences": len(sents)})

    seen = set()
    for s in sents:
        low = s.lower()
        hits = []
        consumed = []
        for alias, name, brand, seg in ALIASES:
            i = low.find(alias)
            if i < 0:
                continue
            if any(i < e and i + len(alias) > b for b, e in consumed):
                continue
            consumed.append((i, i + len(alias)))
            hits.append(name)
        if not hits or len(hits) > 3:
            continue  # 모델 나열 문장(내비게이션) 제외
        key = (tuple(hits), re.sub(r"\W", "", s)[:80])
        if key in seen:
            continue
        seen.add(key)
        p, n = score_text(s)
        for name in hits:
            records.append({
                "source": f.stem, "kind": kind, "model": name,
                "pos": p, "neg": n, "sentence": s[:400],
            })

df = pd.DataFrame(records)
if df.empty:
    raise SystemExit("매칭 없음")
df["sentiment"] = ((df["pos"] - df["neg"]) / (df["pos"] + df["neg"] + 1)).round(3)
df.to_csv("data/mentions.csv", index=False, encoding="utf-8-sig")

# ---- 집계
rows = []
for name, sub in df.groupby("model"):
    ev = sub[(sub.pos + sub.neg) > 0]           # 감성 근거가 있는 문장
    p, n = int(ev.pos.sum()), int(ev.neg.sum())
    if p + n >= 3:
        sat = round(p / (p + n) * 100, 1)
    else:
        sat = None                                # 표본 부족
    brand, seg = MODEL_META[name]
    rows.append({
        "model": name, "brand": brand, "segment": seg,
        "mentions": len(sub), "opinion_mentions": len(ev),
        "sources": sub.source.nunique(),
        "expert_sources": sub[sub.kind.isin(["expert_ko", "expert_en", "lab_en"])].source.nunique(),
        "user_sources": sub[sub.kind.isin(["user_ko", "user_en"])].source.nunique(),
        "pos": p, "neg": n, "satisfaction": sat,
        "avg_tone": round(sub.sentiment.mean(), 3),
    })

g = pd.DataFrame(rows)
mx = math.log1p(g.mentions.max())
g["attention"] = (g.mentions.apply(lambda x: math.log1p(x)) / mx * 100).round(1)
g["coverage"] = (g.sources / len(source_stats) * 100).round(1)
g["satisfaction_f"] = g.satisfaction.fillna(50.0)
g["score"] = (0.45 * g.satisfaction_f + 0.35 * g.attention + 0.20 * g.coverage).round(1)
g.loc[g.mentions < 3, "score"] = None
g = g.sort_values(["score", "mentions"], ascending=[False, False])
g.to_csv("data/summary.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(source_stats).to_csv("data/sources.csv", index=False, encoding="utf-8-sig")

# ---- 내가 읽을 근거 문장 모아두기
with open("data/evidence.txt", "w", encoding="utf-8") as fh:
    for name in g["model"]:
        sub = df[(df.model == name) & ((df.pos + df.neg) > 0)]
        fh.write(f"\n\n{'='*70}\n## {name}  (언급 {len(df[df.model==name])} / 의견 {len(sub)})\n")
        for _, r in sub.sort_values("sentiment", ascending=False).head(12).iterrows():
            fh.write(f"[{r.kind}|{r.sentiment:+.2f}] {r.sentence}\n")

print(f"소스 {len(source_stats)}개 · 문장 {sum(s['sentences'] for s in source_stats):,} · 매칭 {len(df):,}\n")
print(g[["model", "segment", "mentions", "opinion_mentions", "sources", "satisfaction", "attention", "score"]].to_string(index=False))
