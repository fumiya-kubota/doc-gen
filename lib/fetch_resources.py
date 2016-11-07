from random import choice
from .fetcher.image_fetcher import GoogleImageStore


def fetch_text(length):
    pass


def fetch_graph(number):
    image_store = GoogleImageStore('グラフ')
    return image_store.pop_image(number)


def fetch_image(number):
    themes = [
        GoogleImageStore('風景'),
        GoogleImageStore('写真'),
        GoogleImageStore('アニメ'),
        GoogleImageStore('いらすとや')
    ]
    images = []
    for idx in range(number):
        theme = choice(themes)
        images.extend(theme.pop_image())
    return images


def fetch_mathematical_expression(number):
    image_store = GoogleImageStore('数式')
    return image_store.pop_image(number)


def fetch_handwriting(number):
    keyword = '手書き {}'
    themes = [
        GoogleImageStore(keyword.format('文字')),
        GoogleImageStore(keyword.format('ひらがな')),
        GoogleImageStore(keyword.format('アルファベット')),
        GoogleImageStore(keyword.format('イラスト')),
    ]
    images = []
    for idx in range(number):
        theme = choice(themes)
        images.extend(theme.pop_image())
    return images
