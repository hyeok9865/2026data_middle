import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("deck/index.html", encoding="utf-8").read()


def grab(a, b):
    i = h.find(a)
    if i < 0:
        return f"(not found: {a})"
    j = h.find(b, i)
    return h[i:j]


print("--- SPEC TBODY ---")
print(grab("<tbody>", "</tbody>")[:1100])
print("\n--- PROS_0 (first list) ---")
i = h.find('<div class="box p rv d2">')
print(h[i:i + 900])
print("\n--- leftover artifacts ---")
for w in ["<br", "\u200b", "Tap to unmute", "youtube", "{{", "보여준 8"]:
    print(f"  {w!r}: {h.count(w)}")
