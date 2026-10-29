import pathlib
import re

h = pathlib.Path("deck/index.html").read_text(encoding="utf-8")
scripts = re.findall(r"<script>(.*?)</script>", h, re.S)
for i, s in enumerate(scripts):
    p = pathlib.Path(f"build_check_{i}.js")
    p.write_text(s, encoding="utf-8")
    print(f"script[{i}] {len(s):,} chars -> {p}")
print("canvas:", h.count("<canvas"), "| slides:", len(re.findall(r'<section class="slide', h)))
