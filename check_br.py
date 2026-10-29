import re

h = open("deck/index.html", encoding="utf-8").read()
for m in re.finditer(r"<br[^>]{0,12}>?", h):
    s = max(0, m.start() - 30)
    print(repr(h[s:m.end() + 30]))
