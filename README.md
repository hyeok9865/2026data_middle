# 게이밍 마우스 3파전 — 리뷰 데이터 분석

Firecrawl로 리뷰 38개 소스(약 90만 자)를 수집해 **지슈라2 · Viper V3 Pro · Zowie U2**를 비교 분석한 결과입니다.

**🔗 슬라이드 덱: https://hyeok9865.github.io/gaming-mouse-review-deck/**

---

## 결론 요약

| 지표 | 지슈라2 | Viper V3 Pro | Zowie U2 |
|---|---:|---:|---:|
| 무게 | 60g | **54g** | 60g |
| 폴링레이트 | 2,000Hz | **8,000Hz** | 4,000Hz |
| 만족도 | 72.0% | 72.7% | 100%* |
| 언급량 | **80건** | 39건 | 33건 |
| 근거 소스 | **12개** | 6개 | 4개 |
| 부정문 비율 | 12.5% | **3.4%** | 8.0% |
| 국내가 | 18~22만원 | 17.9~23.9만원 | 약 25~27만원 |

\* Zowie U2의 100%는 표본 4개 소스의 착시입니다.

- **무난·안정** → 지슈라2
- **최경량·최고 폴링** → Viper V3 Pro
- **FPS 몰입·소프트웨어 불필요** → Zowie U2

---

## 산출물

| 파일 | 설명 |
|---|---|
| `docs/index.html` | GitHub Pages 배포용 슬라이드 덱 |
| `deck/index.html` | 동일 덱 (로컬 실행용) |
| `deck/data.json` | 덱에 주입되는 비교 데이터 |
| `report.md` | 전체 리뷰 분석 리포트 |
| `게이밍마우스_리뷰분석.xlsx` | 요약 / 근거문장(420) / 소스(38) / 가격 4시트 |
| `data/summary.csv` | 모델별 종합 점수 |
| `data/mentions.csv` | 문장 단위 근거 420건 |
| `data/deepdive.csv` | 3종 심층 비교 수치 |

## 파이프라인

```bash
01_search.py     # Firecrawl 검색 (1차)
02_probe.py      # 소스 스크래핑 가능 여부 확인
03_search2.py    # 모델별 검색 (2차)
04_collect.py    # 본문 수집
05_collect2.py   # 추가 소스 수집
06_analyze.py    # 모델 인식 + 감성 분석
07_search3.py    # 사용 후기 집중 검색
08_collect3.py   # 후기 수집
09_extract.py    # 장단점/가격 추출
10_export.py     # 엑셀 생성
11_deepdive.py   # 3종 심층 비교 데이터
12_build_deck.py # 슬라이드 덱 빌드
13_images.py     # Nano Banana 이미지 생성 시도 (무료 티어 할당량 0으로 미사용)
```

```bash
pip install firecrawl-py pandas openpyxl python-dotenv google-genai
echo "FIRECRAWL_API_KEY=fc-..." > .env
python 06_analyze.py && python 11_deepdive.py && python 12_build_deck.py
```

## 데이터 수집 · 분석 방법

- **수집**: Firecrawl `search` + `scrape` → 38개 소스, 2,685개 문장
- **대상**: 국내 커뮤니티/블로그 27 · 해외 리뷰매체 6 · 제조사성 리뷰 5
- **감성 판정**: 한/영 감성어 사전 + 부정어 처리(`~지 않다`, `없다`)
- **점수식**: `0.45 × 만족도 + 0.35 × 언급량(로그) + 0.20 × 소스 다양성`
- **제외**: Reddit(Firecrawl 미지원), YouTube/Instagram/TikTok(본문 없음)

## 한계

- 수집 문서 중 다수가 **제품 대여·원고료·제휴링크**를 명시 → 만족도 상향 편향
- 표본 불균형 (지슈라2 33건 vs Zowie 10건). 소표본 100%는 신뢰 불가
- 사전 기반 감성분석이라 반어·비교문 처리에 한계
- **Reddit 제외**로 해외 실사용자 반응이 빠져 있음
- 가격은 2026년 5~10월 수집가 기준
- AI 이미지 미사용 (Gemini 무료 티어 이미지 할당량 0) → 비주얼은 CSS·SVG·Chart.js
