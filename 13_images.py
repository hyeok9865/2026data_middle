"""13단계: Nano Banana(Gemini Image)로 슬라이드 에셋 생성."""
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

OUT = Path("deck/assets")
OUT.mkdir(parents=True, exist_ok=True)

MODELS = ["gemini-3-pro-image", "gemini-3.1-flash-image", "gemini-2.5-flash-image"]

BASE = (
    "Photorealistic product photography, cinematic studio lighting, dark charcoal background, "
    "subtle volumetric haze, high detail, shallow depth of field, 8k, no text, no logos, no branding, "
    "no visible trademarks. "
)

JOBS = [
    ("hero", "16:9",
     BASE + "Three modern wireless gaming mice standing on a glossy black reflective surface, "
     "arranged in a row at a slight angle, viewed from a low three-quarter angle. "
     "Rim lighting in cyan on the left mouse, magenta on the middle mouse, lime green on the right mouse. "
     "Futuristic data-visualization atmosphere with faint glowing grid lines in the background."),
    ("mouse-a", "1:1",
     BASE + "Top-down view of a single minimal symmetric white gaming mouse with two main buttons "
     "and a scroll wheel, clean matte plastic, cyan rim light glowing on its edges, floating above a dark surface."),
    ("mouse-b", "1:1",
     BASE + "Three-quarter view of a single low-profile black symmetric gaming mouse, ultra lightweight design, "
     "magenta rim light glowing on its edges, floating above a dark surface."),
    ("mouse-c", "1:1",
     BASE + "Three-quarter view of a single ergonomic symmetric gaming mouse in dark grey, "
     "sculpted side curves, lime green rim light glowing on its edges, floating above a dark surface."),
    ("texture", "16:9",
     "Abstract dark technology background, fine glowing grid of thin cyan lines fading into black, "
     "soft magenta and lime light blooms in the corners, subtle noise, depth of field blur, no text, no objects."),
]

def generate(name: str, ratio: str, prompt: str) -> bool:
    for model in MODELS:
        for attempt in range(2):
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(aspect_ratio=ratio),
                    ),
                )
                for cand in (resp.candidates or []):
                    for part in (cand.content.parts or []):
                        data = getattr(getattr(part, "inline_data", None), "data", None)
                        if data:
                            (OUT / f"{name}.png").write_bytes(data)
                            print(f"[OK ] {name}.png  ({len(data)//1024} KB) via {model}")
                            return True
                print(f"[WARN] {name}: no image part ({model})")
            except Exception as e:  # noqa: BLE001
                msg = str(e)[:180]
                print(f"[ERR ] {name} via {model}: {type(e).__name__}: {msg}")
                if "429" in msg or "quota" in msg.lower() or "RESOURCE_EXHAUSTED" in msg:
                    time.sleep(12)
                else:
                    break
        time.sleep(1)
    return False


ok = 0
for name, ratio, prompt in JOBS:
    if (OUT / f"{name}.png").exists():
        print(f"[SKIP] {name}.png")
        ok += 1
        continue
    if generate(name, ratio, prompt):
        ok += 1
    time.sleep(2)

print(f"\n생성 {ok}/{len(JOBS)}")
sys.exit(0 if ok == len(JOBS) else 1)
