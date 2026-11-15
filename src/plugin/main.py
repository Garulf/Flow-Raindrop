from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Any, List

import httpx
from pyflowlauncher import Plugin, Result

from raindrop import Item, Raindrop
from results import context_menu_results, error_result, init_result, query_results, settings_result

CACHE_TTL = {
    "5 minutes": 300,
    "15 minutes": 900,
    "30 minutes": 1800,
    "1 hour": 3600,
    "6 hours": 21600,
    "12 hours": 43200,
    "1 day": 86400,
    "3 days": 259200,
}

DEFAULT_CACHE_TTL = CACHE_TTL["5 minutes"]

# Flow Launcher runs the plugin from its install folder, where earlier releases kept the cache.
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"

plugin = Plugin()


def cache_ttl() -> int:
    return CACHE_TTL.get(plugin.settings.get("cache_ttl"), DEFAULT_CACHE_TTL)


def raindrop() -> Raindrop:
    return Raindrop(plugin.settings["api_token"], cache_ttl(), CACHE_DIR / "hishel")


def search(query: str) -> List[Item]:
    return raindrop().search(query)


def request_error_results(error: httpx.HTTPError) -> List[Result]:
    icons = plugin.launcher.icons
    if isinstance(error, httpx.HTTPStatusError) and error.response.status_code == 401:
        return [settings_result(
            icons,
            "Raindrop.io rejected the API token",
            "Check the API token in plugin settings.",
        )]
    return [error_result(icons, "Could not search Raindrop.io", str(error))]


@plugin.on_method
async def query(query: str) -> List[Result]:
    if not plugin.settings.get("api_token"):
        return [init_result(plugin.launcher.icons)]
    if not query:
        return []
    loop = asyncio.get_running_loop()
    try:
        items = await loop.run_in_executor(None, search, query)
    except httpx.HTTPError as error:
        return request_error_results(error)
    return query_results(items)


@plugin.on_method
def clear_cache() -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


@plugin.on_method
def context_menu(data: Any) -> List[Result]:
    return context_menu_results(plugin.launcher.icons, clear_cache)
