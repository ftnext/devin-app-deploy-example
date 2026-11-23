# /// script
# dependencies = ["playwright"]
# ///

import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OG_IMAGES = ROOT / "og"


def capture_slides(url: str, output: Path) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        page.goto(url)
        page.wait_for_function("() => window.Reveal?.isReady()")
        indices = page.evaluate(
            """() => Reveal.getSlides().map(slide => {
                const { h, v = 0 } = Reveal.getIndices(slide);
                return [h, v];
            })"""
        )
        if not indices:
            raise RuntimeError("Reveal.js did not find any slides")
        for h, v in indices:
            page.evaluate("([h, v]) => Reveal.slide(h, v)", [h, v])
            page.evaluate("() => document.fonts.ready.then(() => null)")
            page.screenshot(path=output / f"{h}-{v}.png", animations="disabled")
        browser.close()


def main() -> None:
    handler = partial(SimpleHTTPRequestHandler, directory=ROOT / "slides")
    with TemporaryDirectory(dir=ROOT) as temp_dir:
        output = Path(temp_dir)
        with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
            thread = Thread(target=server.serve_forever)
            thread.start()
            try:
                capture_slides(f"http://127.0.0.1:{server.server_port}/", output)
            finally:
                server.shutdown()
                thread.join()

        OG_IMAGES.mkdir(exist_ok=True)
        images = {image.name for image in output.iterdir()}
        for name in sorted(images):
            (output / name).replace(OG_IMAGES / name)
            print(f"og/{name}")
        for image in OG_IMAGES.glob("*.png"):
            if re.fullmatch(r"\d+-\d+\.png", image.name) and image.name not in images:
                image.unlink()


if __name__ == "__main__":
    main()
