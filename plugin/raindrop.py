from enum import Enum
from typing import Dict, Generator, List, TypedDict

import hishel


BASE_URL = 'https://api.raindrop.io/rest/v1'
DEFAULT_CACHE_TTL = 300


class CollectionRef(Enum):
    ALL = 0
    UNSORTED = -1
    TRASH = -99


class Item(TypedDict):
    _id: int
    excerpt: str
    note: str
    type: str
    cover: str
    tags: list
    removed: bool
    title: str
    collection: Dict
    link: str
    created: str
    lastUpdate: str
    important: bool
    media: Dict
    user: Dict
    highlights: List
    domain: str
    creatorRef: Dict
    sort: int
    collectionId: int
    highlight: Dict


class Raindrop:

    def __init__(self, api_token: str, cache_ttl: int = DEFAULT_CACHE_TTL):
        self._api_token = api_token
        self._cache_ttl = cache_ttl

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        storage = hishel.FileStorage(ttl=self._cache_ttl)
        with hishel.CacheClient(storage=storage) as client:
            response = client.request(
                method,
                f'{BASE_URL}/{endpoint}',
                headers={'Authorization': f"Bearer {self._api_token}"},
                extensions={"force_cache": True},
                **kwargs
            )
            response.raise_for_status()
            return response.json()

    def _search(
        self, search: str,
        collection: CollectionRef = CollectionRef.ALL
    ) -> Dict:
        return self._request(
            'GET',
            f'raindrops/{collection.value}',
            params={
                'search': search
            }
        )

    def search(
        self, search: str,
        collection: CollectionRef = CollectionRef.ALL
    ) -> Generator[Item, None, None]:
        yield from self._search(search, collection)['items']
