"""Module for actually getting data and downloading videos from Pornhub."""
import time
import traceback
import requests
import youtube_dl
from youtube_dl.utils import DownloadError
from bs4 import BeautifulSoup


def get_soup(url):
    """Get new soup instance from url."""
    tries = 0
    while True:
        try:
            response = requests.get(url)

            # Couldn't find the site. Stop and return None
            if response.status_code == 404:
                return None

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


def download_video(video_url, name='single_videos'):
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

        time.sleep(6)
    return False, None
