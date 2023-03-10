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
    return re.sub('[^-_.a-z0-9A-Z ]', '', strip_tags(txt), flags=re.IGNORECASE).strip()


def get_articles() -> Generator[dict, None, None]:
    get_url = MAIN_URL
    while True:
        response = session.get(get_url).json()

        next_sinceid = response['data']['cardlistInfo']['since_id']

        cards = response['data']['cards']
        if not cards:
            break

        yield from iter(cards)

        # Next page: https://m.weibo.cn/api/container/getIndex?type=uid&value=1728744882&containerid=1076031728744882&since_id=4872609831323015
        get_url = MAIN_URL + f'&since_id={next_sinceid}'


def interpret_videos():
    for card in get_articles():
        text = card['mblog']['text']
        english_word = _keep_ascii_chars(text)
        posted = parse(card['mblog']['created_at'])
        video_info = card['mblog']['page_info']
        assert video_info['type'] == 'video'
        img = video_info['page_pic']['url']
        extension = img.rsplit('.', 1)[-1]
        video = video_info['media_info']['stream_url_hd']
        video_extension = video.split('?')[0].rsplit('.')[-1]

        # Store it
        img_target = Path(__file__).parent / f'videos/{posted:%Y%m}/{posted:%Y%m%d}_{english_word}.{extension}'
        if img_target.exists():
            continue  # No need to re-download it!

        img_target.parent.mkdir(parents=True, exist_ok=True)

        # JSON
        img_target.with_suffix('.json').write_text(json.dumps(card, indent=4), encoding='utf8')

        # Image
        response = session.get(img, headers={'Referer': 'https://m.weibo.cn/'})
        assert response
        img_target.write_bytes(response.content)

        # Video
        response = session.get(video)
        assert response
        vid_target = img_target.with_suffix(f'.{video_extension}')
        vid_target.write_bytes(response.content)


if __name__ == '__main__':
    interpret_videos()
