from html.parser import HTMLParser
from struct import unpack
from urllib.parse import urljoin

from fastapi.testclient import TestClient

from app import app


class Metadata(HTMLParser):
    def __init__(self, html: str):
        super().__init__()
        self.tags = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            attrs = dict(attrs)
            key = attrs.get("property") or attrs.get("name")
            if key:
                self.tags[key] = attrs["content"]


def test_share_page(monkeypatch):
    monkeypatch.delenv("BASE_URL", raising=False)
    response = TestClient(app).get("/share/1/1", follow_redirects=False)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert Metadata(response.text).tags == {
        "og:type": "website",
        "og:title": "Devin App Deploy Example — スライド 1/1",
        "og:description": "Reveal.js のスライド 1/1 を表示します。",
        "og:url": "http://testserver/share/1/1",
        "og:image": "http://testserver/og/1-1.png",
        "og:image:width": "1200",
        "og:image:height": "630",
        "twitter:card": "summary_large_image",
        "twitter:title": "Devin App Deploy Example — スライド 1/1",
        "twitter:image": "http://testserver/og/1-1.png",
    }
    assert 'href="../../#/1/1"' in response.text
    assert 'location.replace("../../#/1/1")' in response.text


def test_share_page_under_path_prefix():
    response = TestClient(app, root_path="/deck").get("/deck/share/1/1")

    assert response.status_code == 200
    target = "../../#/1/1"
    assert f'href="{target}"' in response.text
    assert f'location.replace("{target}")' in response.text
    assert urljoin(str(response.url), target) == "http://testserver/deck/#/1/1"


def test_base_url_override(monkeypatch):
    monkeypatch.setenv("BASE_URL", "https://slides.example.com/deck/")
    response = TestClient(app).get("/share/1/1")
    tags = Metadata(response.text).tags

    assert tags["og:url"] == "https://slides.example.com/deck/share/1/1"
    assert tags["og:image"] == "https://slides.example.com/deck/og/1-1.png"


def test_missing_slide():
    client = TestClient(app)

    assert client.get("/share/99/99").status_code == 404
    assert client.get("/og/99-99.png").status_code == 404


def test_png():
    response = TestClient(app).get("/og/1-1.png")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert unpack(">II", response.content[16:24]) == (1200, 630)


def test_slide_deck():
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "<title>Devin App Deploy Example</title>" in response.text
    assert "Reveal.initialize" in response.text
