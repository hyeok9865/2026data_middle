"""12단계(v2): 템플릿 + 데이터 -> index.html

스펙 표와 장단점 목록을 빌드 시점에 정적 HTML로 렌더링한다.
(Chart.js/CDN이 막히거나 JS가 실패해도 텍스트는 항상 보이게 하기 위함)
"""
import html
import json
import re
from pathlib import Path

tpl = Path("deck/template.html").read_text(encoding="utf-8")
data = json.loads(Path("deck/data.json").read_text(encoding="utf-8"))
models = data["models"]


def parse_num(s: str):
    s = str(s).replace(",", "")
    m = re.search(r"\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else None


def render_spec_rows() -> str:
    out = []
    for row in data["comparison_rows"]:
        winner = -1
        if row["best"]:
            nums = [parse_num(v) for v in row["values"]]
            idx = [(v, i) for i, v in enumerate(nums) if v is not None]
            if len(idx) == 3:
                target = min(v for v, _ in idx) if row["best"] == "min" else max(v for v, _ in idx)
                winner = next(i for v, i in idx if v == target)
        cells = "".join(
            f'<td class="{"win" if i == winner else ""}">{html.escape(v)}</td>'
            for i, v in enumerate(row["values"])
        )
        out.append(f"<tr><td>{html.escape(row['label'])}</td>{cells}</tr>")
    return "\n      ".join(out)


def render_items(items) -> str:
    return "".join(
        f'<li><span class="basis" data-b="{html.escape(it["basis"])}">{html.escape(it["basis"])}</span>'
        f'{html.escape(it["t"])}</li>'
        for it in items
    )


notes = (
    "폴링 · " + " / ".join(f"{m['name']} {m['spec']['polling_note']}" for m in models)
    + "<br>배터리 · " + " / ".join(f"{m['name']} {m['spec']['battery_note']}" for m in models)
)

html_out = tpl.replace("{{SPEC_ROWS}}", render_spec_rows())
html_out = html_out.replace("{{SPEC_NOTES}}", notes)
for i, m in enumerate(models):
    html_out = html_out.replace(f"{{{{PROS_{i}}}}}", render_items(m["pros"]))
    html_out = html_out.replace(f"{{{{CONS_{i}}}}}", render_items(m["cons"]))

payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
html_out = html_out.replace("/*__DATA__*/{}", payload)

leftover = re.findall(r"\{\{[A-Z_0-9]+\}\}", html_out)
if leftover:
    raise SystemExit(f"치환되지 않은 플레이스홀더: {set(leftover)}")
if "__DATA__" in html_out:
    raise SystemExit("데이터 주입 실패")

Path("deck/index.html").write_text(html_out, encoding="utf-8")
docs = Path("docs")
docs.mkdir(exist_ok=True)
(docs / "index.html").write_text(html_out, encoding="utf-8")
(docs / ".nojekyll").write_text("", encoding="utf-8")

print(f"deck/index.html + docs/index.html 생성 ({len(html_out):,} bytes)")
print(f"  스펙 {len(data['comparison_rows'])}행 · 모델 {len(models)}종")
for m in models:
    print(f"  - {m['name']}: pros {len(m['pros'])} / cons {len(m['cons'])}")
