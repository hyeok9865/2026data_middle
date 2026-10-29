"""10단계: 결과 엑셀 정리."""
from pathlib import Path

import pandas as pd

summ = pd.read_csv("data/summary.csv")
ment = pd.read_csv("data/mentions.csv")
src = pd.read_csv("data/sources.csv")
price = pd.read_csv("data/price_spec.csv")

# 리포트용 가격(수집 원문에서 확인된 한국 시장 실판매가 구간)
PRICE = {
    "Logitech G102 / G203": "2.6~3.1만원",
    "Logitech G304 / G305": "3~4만원",
    "Logitech G309": "7~8만원",
    "Logitech G502 X": "9~11만원",
    "Logitech G PRO X SUPERLIGHT": "18~22만원",
    "Logitech G PRO X SUPERLIGHT 2": "18~22만원",
    "Logitech G PRO X SUPERLIGHT 2 DEX": "18~22만원",
    "Logitech G PRO 2 / SUPERSTRIKE": "국내가 확인 필요",
    "Razer DeathAdder V3 Pro": "11~14만원",
    "Razer DeathAdder V4 Pro": "23~27만원",
    "Razer Viper V3 Pro": "17.9~23.9만원",
    "Razer Viper V4 Pro": "국내가 확인 필요",
    "Razer Basilisk V3 Pro": "국내가 확인 필요",
    "ATK / VXE (잠자리)": "2만원대(SE+)",
    "Zowie U2": "국내가 확인 필요",
    "Lamzu Maya X": "국내가 확인 필요",
    "Pulsar X2 / X2V2": "국내가 확인 필요",
    "VAXEE XE / XE V2": "국내가 확인 필요",
    "Ninjutso Sora": "국내가 확인 필요",
    "Endgame Gear OP1": "국내가 확인 필요",
    "Corsair Sabre V3 Pro": "국내가 확인 필요",
}
summ["korea_price"] = summ.model.map(PRICE).fillna("-")

# 전문가 픽 (RTINGS 2026-09-29 기준 + 노써치)
EXPERT = {
    "Logitech G PRO 2 / SUPERSTRIKE": "RTINGS 최우수 무선 게이밍",
    "Logitech G PRO X SUPERLIGHT 2": "RTINGS 무선 2순위 (로지텍=국내 판매 1위 브랜드)",
    "Razer Viper V4 Pro": "RTINGS 상위중급 1순위",
    "Razer Viper V3 Pro": "RTINGS 상위중급 2순위",
    "Logitech G502 X": "RTINGS 중급 1순위",
    "Logitech G304 / G305": "RTINGS 최저가 부문 1순위",
    "Zowie U2": "국내 FPS 커뮤니티 선호",
    "ATK / VXE (잠자리)": "국내 가성비 대표",
}
summ["expert_note"] = summ.model.map(EXPERT).fillna("")

order = ["model", "brand", "segment", "korea_price", "score", "satisfaction",
         "mentions", "opinion_mentions", "sources", "attention", "coverage", "expert_note"]
summ = summ[order].sort_values("score", ascending=False, na_position="last")

with pd.ExcelWriter("게이밍마우스_리뷰분석.xlsx", engine="openpyxl") as xl:
    summ.to_excel(xl, sheet_name="요약", index=False)
    ment.to_excel(xl, sheet_name="근거문장", index=False)
    src.to_excel(xl, sheet_name="수집소스", index=False)
    price.to_excel(xl, sheet_name="가격추출", index=False)

print(summ.head(12).to_string(index=False))
print("\n-> 게이밍마우스_리뷰분석.xlsx")
