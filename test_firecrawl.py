"""Firecrawl 연결 테스트."""
import os
import sys

from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")
if not api_key:
    sys.exit("FIRECRAWL_API_KEY 가 .env 에 없습니다.")

app = Firecrawl(api_key=api_key)
doc = app.scrape("https://example.com", formats=["markdown"])

markdown = getattr(doc, "markdown", None) or ""
meta = getattr(doc, "metadata", None)
title = getattr(meta, "title", None) if meta is not None else None

lines = [
    f"key_prefix={api_key[:6]}...{api_key[-4:]} (len={len(api_key)})",
    f"title={title}",
    f"markdown_len={len(markdown)}",
    "--- markdown head ---",
    markdown[:300],
]

with open("test_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("OK -> test_result.txt")
