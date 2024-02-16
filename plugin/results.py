from __future__ import annotations
from typing import TYPE_CHECKING, Generator

from pyflowlauncher import Result
from pyflowlauncher.api import open_url, open_setting_dialog
from pyflowlauncher.icons import RECYCLEBIN, SETTINGS, LINK


if TYPE_CHECKING:
    from raindrop import Raindrop, Item


def init_results() -> Result:
    return Result(
        Title="No API token found!",
        SubTitle="Please enter your Raindrop.io API token in plugin settings.",
        IcoPath=SETTINGS,
        JsonRPCAction=open_setting_dialog()
    )


def query_result(item: Item) -> Result:
    return Result(
        Title=item["title"],
        SubTitle=item["excerpt"],
        IcoPath=item["cover"],
        ContextData=[],
        JsonRPCAction=open_url(item["link"])
    )


def query_results(
    raindrop: Raindrop,
    query: str
) -> Generator[Result, None, None]:
    search = raindrop.search(query)
    for item in search:
        yield query_result(item)


def context_menu_results() -> Generator[Result, None, None]:
    yield Result(
        Title="Open Raindrop.io",
        SubTitle="Open Raindrop.io in your browser",
        IcoPath=LINK,
        JsonRPCAction=open_url("https://raindrop.io")
    )
    yield Result(
        Title="Clear cached data",
        SubTitle="All cached data will be removed",
        IcoPath=RECYCLEBIN,
        JsonRPCAction={
            "method": "clear_cache",
            "parameters": [],
        }
    )
