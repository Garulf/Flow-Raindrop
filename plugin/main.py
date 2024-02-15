from pyflowlauncher import Plugin, ResultResponse, send_results
from pyflowlauncher.settings import settings
from pyflowlauncher.utils import score_results


from raindropio import API, CollectionRef
import requests_cache

from results import query_results

plugin = Plugin()


@plugin.on_method
def query(query: str) -> ResultResponse:
    requests_cache.install_cache(".cache", backend="sqlite", expire_after=300)
    api_token = settings().get('api_token')
    rain_api = API(api_token)
    collection_setting = settings().get('default_collection', 'All Collections')
    collection = {
        "All Collections": CollectionRef({"$id": 0}),
        "Unsorted": CollectionRef.Unsorted
    }.get(collection_setting)
    return send_results(
        score_results(
            query,
            query_results(rain_api, collection),
        )
    )
