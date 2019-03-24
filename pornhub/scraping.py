"""Module for actually getting data and downloading videos from Pornhub."""
import time
import traceback
import requests
import youtube_dl
from bs4 import BeautifulSoup

from pornhub.helper import get_user_video_url


def get_soup(url):
    """Get new soup instance from url."""
    tries = 0
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except BaseException as e:
            print('Got exception during html fetch.')
            traceback.print_exc()
            time.sleep(60)
            tries += 1

            if tries > 3:
                raise e
            continue

        return soup


def get_user_video_viewkeys(user):
    """Scrape all chapters of the story and write it to a file."""
    url = get_user_video_url(user.user_type, user.key)
    soup = get_soup(url)

    navigation = soup.find_all('div', {'class': 'pagination3'})[0]
    if len(navigation) >= 1:
        children = navigation.findChildren('li', {'class': 'page_number'})
        pages = len(children) + 1
    else:
        pages = 1

    keys = []
    current_page = 1
    next_url = url
    while current_page <= pages:
        print(f'Crawling {next_url}')
        videos = soup.find(id='mostRecentVideosSection')

        for video in videos.find_all('li'):
            keys.append(video['_vkey'])

        current_page += 1
        next_url = url + f'?pages={current_page}'

        time.sleep(2)
        soup = get_soup(next_url)

    return keys


def download_video(video_url, name='default'):
    """Download the video."""
    options = {
        'outtmpl': f'~/pornhub/{name}/%(title)s.%(ext)s',
        'format': 'best',
    }
    ydl = youtube_dl.YoutubeDL(options)
    tries = 0
    while True:
        try:
            info = ydl.extract_info(video_url)
            return info
        except TypeError as e:
            # This is an error that seems to occurr from time to time
            # A short wait and retry often seems to fix the problem
            # This is something about pornhub not properly loading the video.
            time.sleep(2)
            tries += 1

            # If this happens too many times, something else must be broken.
            if tries > 10:
                raise e
            continue

        time.sleep(20)
        return
