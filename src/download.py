import json
import re
from pathlib import Path
from typing import Generator

import bs4
import requests
from dateutil.parser import parse

MAIN_URL = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=1728744882&containerid=1076031728744882'
STRIP_TAGS = re.compile('<.*?>')

session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'


def strip_tags(txt):
    return bs4.BeautifulSoup(txt).text


def _keep_ascii_chars(txt):
    txt = re.sub('[^-_.,a-z0-9A-Z ]', '', strip_tags(txt), flags=re.IGNORECASE)
    txt = txt.strip(' ,.-_')  # Remove extra chars
    txt = re.sub(' +', ' ', txt)  # remove double spaces
    return txt


def get_articles() -> Generator[dict, None, None]:
    get_url = MAIN_URL
    while True:
        response = session.get(get_url).json()

        cards = response['data']['cards']
        if not cards:
            break

        yield from iter(cards)

        try:
            next_sinceid = response['data']['cardlistInfo']['since_id']
        except KeyError:
            break

        # Next page: https://m.weibo.cn/api/container/getIndex?type=uid&value=1728744882&containerid=1076031728744882&since_id=4872609831323015
        get_url = MAIN_URL + f'&since_id={next_sinceid}'


def interpret_videos():
    for card in get_articles():
        text = card['mblog']['text']
        english_word = _keep_ascii_chars(text)
        if not english_word:
            # TODO: translate it?
            ...

        posted = parse(card['mblog']['created_at'])

        # Save the JSON file
        json_target = Path(__file__).parent / f'../html/videos/{posted:%Y%m}/{posted:%Y%m%d}_{english_word[:50]}.json'
        json_target.parent.mkdir(parents=True, exist_ok=True)
        if json_target.exists():
            continue

        json_target.write_text(json.dumps(card, indent=4), encoding='utf8')

        if 'page_info' not in card['mblog']:
            continue

        video_info = card['mblog']['page_info']
        if video_info['type'] != 'video':
            continue

        # Image
        img = video_info['page_pic']['url']
        extension = img.rsplit('.', 1)[-1]
        response = session.get(img, headers={'Referer': 'https://m.weibo.cn/'})
        assert response
        json_target.with_suffix(f'.{extension}').write_bytes(response.content)

        # Video
        urls = [
            video_info['media_info']['stream_url_hd'],
            video_info['media_info']['stream_url'],
        ]
        urls.extend(video_info['urls'].values())
        for video in urls:
            response = session.get(video)
            if not response:
                continue

            video_extension = video.split('?')[0].rsplit('.')[-1]
            json_target.with_suffix(f'.{video_extension}').write_bytes(response.content)
            break


if __name__ == '__main__':
    interpret_videos()
