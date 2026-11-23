# /// script
# dependencies = ["fastapi>=0.138.0", "uvicorn"]
# ///

import os
import re
from html import escape, unescape
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse

ROOT = Path(__file__).resolve().parent
SLIDES = ROOT / "slides"
OG_IMAGES = ROOT / "og"
DECK_TITLE = unescape(
    re.search(r"<title>(.*?)</title>", (SLIDES / "index.html").read_text(encoding="utf-8"))
    .group(1)
    .strip()
)

app = FastAPI()


def slide_image(h: int, v: int) -> Path:
    path = OG_IMAGES / f"{h}-{v}.png"
    if h < 0 or v < 0 or not path.is_file():
        raise HTTPException(status_code=404, detail="Slide not found")
    return path


@app.get("/og/{h}-{v}.png", response_class=FileResponse)
def og_image(h: int, v: int) -> FileResponse:
    return FileResponse(slide_image(h, v), media_type="image/png")


@app.get("/share/{h}/{v}", response_class=HTMLResponse)
def share_slide(request: Request, h: int, v: int) -> str:
    image = slide_image(h, v)
    base = (os.environ.get("BASE_URL") or str(request.base_url)).rstrip("/")
    title = escape(f"{DECK_TITLE} — スライド {h}/{v}")
    description = f"Reveal.js のスライド {h}/{v} を表示します。"
    share_url = escape(f"{base}/share/{h}/{v}")
    image_url = escape(f"{base}/og/{image.name}")
    slide_url = f"../../#/{h}/{v}"
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{share_url}">
  <meta property="og:image" content="{image_url}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:image" content="{image_url}">
</head>
<body>
  <a href="{slide_url}">スライドを開く</a>
  <script>location.replace("{slide_url}");</script>
</body>
</html>"""


app.frontend("/", directory=SLIDES)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
    )
