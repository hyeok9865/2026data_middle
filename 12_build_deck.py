"""12단계: 템플릿 + 데이터 -> index.html"""
import json
from pathlib import Path

tpl = Path("deck/template.html").read_text(encoding="utf-8")
data = json.loads(Path("deck/data.json").read_text(encoding="utf-8"))

payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
html = tpl.replace("/*__DATA__*/{}", payload)

# 안전 장치: 플레이스홀더가 남아있으면 실패
if "__DATA__" in html:
    raise SystemExit("데이터 주입 실패")

Path("deck/index.html").write_text(html, encoding="utf-8")

# GitHub Pages 배포용 (/docs 를 Pages 소스로 사용)
docs = Path("docs")
docs.mkdir(exist_ok=True)
(docs / "index.html").write_text(html, encoding="utf-8")
(docs / ".nojekyll").write_text("", encoding="utf-8")

print(f"deck/index.html + docs/index.html 생성 ({len(html):,} bytes)")
print(f"  모델: {[m['name'] for m in data['models']]}")
print(f"  스펙 행: {len(data['comparison_rows'])}")
