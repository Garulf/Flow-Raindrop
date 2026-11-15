from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List

from pyflowlauncher import Result
from pyflowlauncher.api import open_setting_dialog, open_url
from pyflowlauncher.icons import Icons
from pyflowlauncher.types import Method

if TYPE_CHECKING:
    from raindrop import Item

RAINDROP_URL = "https://raindrop.io"


def settings_result(icons: Icons, title: str, subtitle: str) -> Result:
    return Result(
        title=title,
        subtitle=subtitle,
        icon=icons.settings,
    ).add_action(open_setting_dialog())


def init_result(icons: Icons) -> Result:
    return settings_result(
        icons,
        "No API token found!",
        "Please enter your Raindrop.io API token in plugin settings.",
    )


def error_result(icons: Icons, title: str, subtitle: str) -> Result:
    return Result(title=title, subtitle=subtitle, icon=icons.error)


def query_result(item: Item) -> Result:
    return Result(
        title=item["title"],
        subtitle=item.get("excerpt"),
        icon=item.get("cover"),
        context_data=[],
    ).add_action(open_url(item["link"]))


def query_results(items: Iterable[Item]) -> List[Result]:
    return [query_result(item) for item in items]


def context_menu_results(icons: Icons, clear_cache: Method) -> List[Result]:
    return [
        Result(
            title="Open Raindrop.io",
            subtitle="Open Raindrop.io in your browser",
            icon=icons.link,
        ).add_action(open_url(RAINDROP_URL)),
        Result(
            title="Clear cached data",
            subtitle="All cached data will be removed",
            icon=icons.recyclebin,
        ).add_action(clear_cache),
    ]
