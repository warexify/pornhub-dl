"""Module for actually getting data and downloading videos from Pornhub."""
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time
import youtube_dl

from pornhub.models import User

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36',
    'cache-control': 'no-cache',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, sdch, br',
    'accept-language': 'en-US,en;q=0.8,de;q=0.6,ru;q=0.4,id;q=0.2',
    'dnt': 1,
    'pragma': 'no-cache',
    'upgrade-insecure-requests': 1,
}


def get_soup(url):
    """Get new soup instance from url."""
    tries = 0
    while True:
        try:
            page = urlopen(url)
            soup = BeautifulSoup(page, 'html.parser')
        except BaseException as e:
            print('Got exception during html fetch.')
            time.sleep(60)
            tries += 1

            if tries > 3:
                raise e
            continue

        return soup


def get_video_urls(url):
    """Scrape all chapters of the story and write it to a file."""
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

    urls = []
    for key in keys:
        urls.append(f'https://www.pornhub.com/view_video.php?viewkey={key}')

    return urls


def get_name(url, mode):
    """Get the name of the user by website."""
    soup = get_soup(url)
    if mode == User.CHANNEL:
        section = soup.find_all('section', {'class': 'channelsProfile'})[0]
        wrapper = section.find_all('div', {'class': 'bottomExtendedWrapper'})[0]
        h1 = wrapper.find_all('h1')[0]
        a = h1.find_all('a')[0]
        name = a.contents[0]
    elif mode == User.FULL_USER:
        div = soup.find_all('div', {'class': 'nameSubscribe'})[0]
        h1 = div.find_all('h1')[0]
        name = h1.contents[0]
    elif mode == User.SINGLE_VIDEO:
        info = soup.find_all('div', {'class': 'video-detailed-info'})[0]
        wrap = info.find_all('div', {'class': 'usernameWrap'})[0]
        h1 = wrap.find_all('a')[0]
        name = h1.contents[0]

    return name


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
            ydl.download([video_url])
        except BaseException as e:
            print('Got Exception')
            print(e)
            time.sleep(60)
            tries += 1

            if tries > 10:
                raise e
            continue

        time.sleep(20)
        return


