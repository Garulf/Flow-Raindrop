from __future__ import annotations
from typing import TYPE_CHECKING, Generator

from pyflowlauncher import Result
from pyflowlauncher.api import open_url

from raindropio import Raindrop


if TYPE_CHECKING:
    from raindropio import API, CollectionRef


def query_result(raindrop: Raindrop) -> Result:
    return Result(
        Title=raindrop.title,
        SubTitle=raindrop.excerpt,
        IcoPath=raindrop.cover,
        JsonRPCAction=open_url(raindrop.link)
    )


def query_results(
    rain_api: API,
    collection: CollectionRef,
) -> Generator[Result, None, None]:
    search = Raindrop.search(rain_api, collection=collection)
    for item in search:
        yield query_result(item)
