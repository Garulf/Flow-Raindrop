import shutil
from typing import List

from pyflowlauncher import Plugin, ResultResponse, send_results
from pyflowlauncher.settings import settings
from raindrop import Raindrop

from results import query_results, context_menu_results, init_results


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


plugin = Plugin()


@plugin.on_method
def query(query: str) -> ResultResponse:
    api_token = settings().get('api_token')
    cache_ttl = settings().get('cache_ttl', DEFAULT_CACHE_TTL)
    if not api_token:
        return send_results([init_results()])
    if not query:
        return send_results([])
    rd = Raindrop(api_token, CACHE_TTL[cache_ttl])
    return send_results(
        query_results(rd, query)
    )


@plugin.on_method
def context_menu(data: List) -> ResultResponse:
    return send_results(context_menu_results())


@plugin.on_method
def clear_cache() -> None:
    shutil.rmtree('.cache')
