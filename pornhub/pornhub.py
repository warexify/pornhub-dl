#!/bin/env python3
"""A scraper for pornhub."""
from pornhub.scraping import (
    get_video_urls,
    get_name,
    download_video,
)
from pornhub.arguments import parser

FULL_USER = 'user'
SINGLE_VIDEO = 'video'
CHANNEL = 'channel'


def main():
    """Create a new scraper."""
    args = vars(parser.parse_args())

    url = args['url']
    name = args['name']

    if 'viewkey' in url:
        mode = SINGLE_VIDEO
    elif 'model' in url or 'pornstar' in url or 'users' in url:
        mode = FULL_USER
        if not url.endswith('/videos'):
            raise Exception('I need the /videos url for this user')
    elif 'channels' in url:
        mode = CHANNEL
    else:
        raise Exception('Unknown/unsupported url')

    if mode == FULL_USER:
        video_urls = get_video_urls(url)
    elif mode == SINGLE_VIDEO:
        video_urls = [url]
    else:
        raise Exception('Unknown/unsupported mode')

    if not name:
        name = get_name(url, mode)

    name = name.strip()
    print(f'Found {len(video_urls)} videos')
    for video_url in video_urls:
        download_video(video_url, name)
