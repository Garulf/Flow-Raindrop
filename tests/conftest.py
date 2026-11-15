from functools import partial

import httpx
import pytest

import main
from raindrop import Raindrop

TOKEN = "test-token-0000"

ITEMS = [
    {
        "_id": 1,
        "title": "Python asyncio documentation",
        "excerpt": "Asynchronous I/O, event loop, coroutines and tasks.",
        "cover": "https://docs.python.org/3/_static/og-image.png",
        "link": "https://docs.python.org/3/library/asyncio.html",
        "domain": "docs.python.org",
    },
    {
        "_id": 2,
        "title": "Real Python: Async IO walkthrough",
        "excerpt": "",
        "cover": "",
        "link": "https://realpython.com/async-io-python/",
        "domain": "realpython.com",
    },
]


class FakeRaindropApi:
    def __init__(self):
        self.requests = []
        self.status_code = 200
        self.error = None

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        if self.status_code != 200:
            return httpx.Response(self.status_code, json={"result": False, "errorMessage": "Unauthorized"})
        query = request.url.params.get("search", "").lower()
        items = [item for item in ITEMS if query in item["title"].lower()]
        return httpx.Response(200, json={"result": True, "items": items, "count": len(items)})


@pytest.fixture
def settings():
    launcher = main.plugin.launcher
    launcher._settings = {"api_token": TOKEN, "cache_ttl": "5 minutes"}
    yield launcher._settings
    launcher._settings = {}


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "CACHE_DIR", tmp_path / ".cache")
    return tmp_path / ".cache"


@pytest.fixture
def api(settings, cache_dir, monkeypatch):
    fake = FakeRaindropApi()
    monkeypatch.setattr(main, "Raindrop", partial(Raindrop, transport=httpx.MockTransport(fake)))
    return fake
