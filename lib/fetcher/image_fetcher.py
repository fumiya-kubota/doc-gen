from urllib.parse import quote
from requests import get
import json
from random import shuffle, randrange
import yaml

API_ENV = yaml.load(open('env.yaml'))


class GoogleImageStore:
    API_KEY = API_ENV['CSE']['API_KEY']
    SEARCH_ENGINE_ID = API_ENV['CSE']['SEARCH_ENGINE_ID']
    BASE_URL = 'https://www.googleapis.com/customsearch/v1'

    def __init__(self, keyword):
        super().__init__()
        self._keyword = keyword
        self._items = []

    def pop_image(self, number=1):
        while number > len(self._items):
            self._search()
        links = []
        for _ in range(number):
            links.append(self._items.pop())
        return links

    def _search(self):
        search_url = '{}?key={}&cx={}&searchType=image&start={}&q={}'.format(
            self.BASE_URL,
            self.API_KEY,
            self.SEARCH_ENGINE_ID,
            randrange(1, 100, 10),
            quote(self._keyword))

        response = get(search_url).text
        data = json.loads(response)
        items = [d['link'] for d in data['items']]
        shuffle(items)
        self._items.extend(items)
