"""Module for actually getting data and downloading videos from Pornhub."""
import time
import traceback
import requests
import youtube_dl
from youtube_dl.utils import DownloadError
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
    """Scrape all viewkeys of the user's videos."""
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

        time.sleep(20)
        soup = get_soup(next_url)

    return keys


def get_playlist_video_viewkeys(playlist):
    """Scrape all viewkeys of the playlist's videos."""
    url = f'https://www.pornhub.com/playlist/{playlist.id}'
    soup = get_soup(url)

    videos = soup.find_all('ul', {'id': 'videoPlaylist'})[0]

    keys = []
    for video in videos.find_all('li'):
        keys.append(video['_vkey'])

    return keys


def download_video(video_url, name='default'):
    """Download the video."""
    options = {
        'outtmpl': f'~/pornhub/{name}/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
    }
    ydl = youtube_dl.YoutubeDL(options)
    tries = 0
    while True:
        try:
            print(f'Start downloading: {video_url}')
            info = ydl.extract_info(video_url)
            return True, info
        except TypeError:
            # This is an error that seems to occurr from time to time
            # A short wait and retry often seems to fix the problem
            # This is something about pornhub not properly loading the video.
            print('Got TypeError bug')
            time.sleep(20)
            tries += 1

            # If this happens too many times, something else must be broken.
            if tries > 10:
                return False, None
            continue
        except DownloadError:
            # We got a download error.
            # Ignore for now and continue downloading the other videos
            print("DownloadError: Failed to download video.")
            return False, None

        time.sleep(20)
    return False, None
