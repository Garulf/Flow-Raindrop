from flox import Flox, utils, ICON_SETTINGS, ICON_WARNING

from raindropio import API, CollectionRef, Raindrop, Collection
from requests.exceptions import HTTPError

ALL_COLLECTIONS = CollectionRef({"$id": 0})
COLLECTIONS = {
    "All Collections": ALL_COLLECTIONS,
    "Unsorted": CollectionRef.Unsorted
}

def get_tags(api, id=None):

    URL = f"https://api.raindrop.io/rest/v1/tags"
    if id is not None:
        URL = f"{URL}/{id}"

    results = api.get(URL).json()
    return results.get('items', [])

class FlowRainDrop(Flox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_token = self.settings.get('api_token')
        self.logger.warning(f"API_TOKEN: {self.api_token}")
        self.rain_api = API(self.api_token)
        collection_setting = self.settings.get('default_collection', 'All Collections')
        self.collection = COLLECTIONS.get(collection_setting)

    def _query(self, query):
        try:
            self.query(query)
        except HTTPError as e:
            self.logger.error(f"HTTPError: {query}")
            if "401 Client Error" in str(e):
                self.add_item(
                    title='Unable to Authenticate with Raindrop.io',
                    subtitle='Please check your API Token in settings.',
                    icon=ICON_SETTINGS
                )
            else:
                self.add_item(
                    title='Unable to connect to Raindrop.io',
                    subtitle='Please check your internet connection.',
                    icon=ICON_WARNING
                )
        except Exception as e:
            self.logger.error(f"Exception: {query}")
            self.add_item(
                title=e.__class__.__name__,
                subtitle=str(e),
                icon=ICON_WARNING
            )
        return self._results

    def query(self, query):
        page = 0
        words = query.split(' ')
        created_tags = utils.cache('tags.json', max_age=120, dir=self.name)(get_tags)(self.rain_api)
        tag_names = [tag['_id'] for tag in created_tags]
        if words[-1].startswith('#') and words[-1].replace('#', '') not in tag_names:
            self.tag_query(created_tags, words)
        with utils.ThreadPoolExecutor(max_workers=5) as executor:
            while (items:=Raindrop.search(self.rain_api, word=query, collection=self.collection, page=page)):
                for item in items:
                    self.add_item(
                        title=item.title,
                        subtitle=item.link,
                        icon=utils.get_icon(item.cover, self.name, f"{item.id}.jpg", executor=executor),
                        method=self.browser_open,
                        parameters=[item.link],
                    )
                page += 1
        self.logger.warning(query)

    def context_menu(self, data):
        pass

    def tag_query(self, tags, words):
        word = words[-1]
        if len(words) == 1:
            current_query = ''
        else:
            current_query = f"{' '.join(words[:-1])} "
        for tag in tags:
            if word[1:] in tag['_id']:
                title = f"#{tag['_id']}"
                self.add_item(
                    title=title,
                    subtitle=f"Tagged item count: {tag['count']}",
                    icon=self.icon,
                    method=self.change_query,
                    parameters=[f'{self.user_keyword} {current_query}{title} '],
                    dont_hide=True
                )

if __name__ == "__main__":
    FlowRainDrop()
