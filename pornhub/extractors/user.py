"""Helper for extracting meta information from pornhub."""
import re
import os
import time
import requests
from bs4 import BeautifulSoup

from pornhub.models import User, Clip
from pornhub.helper import get_clip_path, symlink_duplicate
from pornhub.download import get_soup, download_video


def download_user_videos(session, user):
    """Download all videos of a user."""
    viewkeys = get_recent_video_viewkeys(user)
    secondary_viewkeys = get_public_user_video_viewkeys(user)
    viewkeys = set(viewkeys + secondary_viewkeys)

    print(f'Found {len(viewkeys)} videos.')
    for viewkey in viewkeys:
        clip = Clip.get_or_create(session, viewkey, user)

        # The clip has already been downloaded, skip it.
        if clip.completed:
            if clip.title is not None and \
               clip.extension is not None:
                target_path = get_clip_path(user.name, clip.title, clip.extension)
                symlink_duplicate(clip, target_path)

            continue

        success, info = download_video(viewkey, user.name)
        if success:
            clip.title = info['title']
            clip.completed = True
            clip.user = user
            clip.location = info['out_path']
            clip.extension = info['ext']

            print(f'New video: {clip.title}')

        session.commit()
        time.sleep(20)


def get_user_video_url(user_type, key):
    """Compile the user videos url."""
    is_premium = os.path.exists('http_cookie_file')
    if is_premium:
        return f'https://www.pornhubpremium.com/{user_type}/{key}'

    return f'https://www.pornhub.com/{user_type}/{key}'


def get_secondary_user_video_url(user_type, key):
    """Check if there is a secondary video url."""
    is_premium = os.path.exists('http_cookie_file')
    if is_premium:
        possible_urls = [
            f'https://www.pornhubpremium.com/{user_type}/{key}/videos/upload',
            f'https://www.pornhubpremium.com/{user_type}/{key}/videos/public',
        ]
    else:
        possible_urls = [
            f'https://www.pornhub.com/{user_type}/{key}/videos/upload',
            f'https://www.pornhub.com/{user_type}/{key}/videos/public',
        ]

    for url in possible_urls:
        response = requests.get(url)
        if response.status_code == 200:
            return url

    print(f'No public/upload site for user {key}.')
    return None


def get_user_info(key):
    """Get all necessary user information."""
    user_type, url, soup = get_user_type_and_url(key)
    name = get_user_name_from_soup(soup, 'user')

    name = name.strip()
    name = name.replace(' ', '_')
    name = re.sub(r'[\W]+', '_', name)

    return {
        'type': user_type,
        'url': url,
        'name': name,
    }


def get_user_type_and_url(key):
    """Detect the user type and the respective url for this user."""
    possible_urls = {}
    for user_type in [User.PORNSTAR, User.MODEL, User.USER]:
        possible_urls[user_type] = get_user_video_url(user_type, key)

    for user_type, url in possible_urls.items():
        response = requests.get(url, allow_redirects=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return user_type, url, soup

    raise Exception(f"Couldn't detect type for user {key}")


def get_user_name_from_soup(soup, website_type):
    """Get the name of the user by website."""
#    if website_type == 'channel':
#        section = soup.find_all('section', {'class': 'channelsProfile'})[0]
#        wrapper = section.find_all('div', {'class': 'bottomExtendedWrapper'})[0]
#        h1 = wrapper.find_all('h1')[0]
#        a = h1.find_all('a')[0]
#        name = a.contents[0]
#
#    elif website_type == 'video':
#        info = soup.find_all('div', {'class': 'video-detailed-info'})[0]
#        wrap = info.find_all('div', {'class': 'usernameWrap'})[0]
#        h1 = wrap.find_all('a')[0]
#        name = h1.contents[0]

    profileHeader = soup.find('section', {'class': 'topProfileHeader'})

    # Try to get the user name from subscription element
    div = profileHeader.find('div', {'class': 'nameSubscribe'})
    if div is not None:
        h1 = div.find('h1')
        return h1.text

    # Try to get the user name  from normal profile
    div = profileHeader.find('div', {'class': 'profileUserName'})
    if div is not None:
        a = div.find('a')
        return a.text

    return None


def get_recent_video_viewkeys(user):
    """Scrape all viewkeys of the user's videos."""
    url = get_user_video_url(user.user_type, user.key)
    soup = get_soup(url)

    keys = []
    current_page = 1
    next_url = url
    while True:
        print(f'Crawling {next_url}')
        # Videos for normal users/models
        videos = soup.find(id='mostRecentVideosSection')

        # Videos for pornstars
        if videos is None:
            videos = soup.find(id='pornstarsVideoSection')

        # User has no most recent videos section
        if videos is None:
            return []

        for video in videos.find_all('li'):
            if video.has_attr('_vkey'):
                keys.append(video['_vkey'])

        current_page += 1
        next_url = url + f'?page={current_page}'

        time.sleep(4)
        soup = get_soup(next_url)
        # We couldn't get the next url.
        if soup is None:
            break

    return keys


def get_public_user_video_viewkeys(user):
    """Scrape all public viewkeys of the user's videos."""
    url = get_secondary_user_video_url(user.user_type, user.key)

    # Couldn't find a public/upload video site
    if url is None:
        return []

    soup = get_soup(url)

    keys = []
    current_page = 1
    next_url = url
    while True:
        print(f'Crawling {next_url}')
        # Videos for normal users/models
        wrapper = soup.find('div', {'class': 'videoUList'})

        # Videos for pornstars
        if wrapper is None:
            videos = soup.find(id='pornstarsVideoSection')
        else:
            videos = wrapper.find('ul')

        if videos is None:
            return []

        for video in videos.find_all('li'):
            if video.has_attr('_vkey'):
                keys.append(video['_vkey'])

        current_page += 1
        next_url = url + f'?page={current_page}'

        time.sleep(4)

        soup = get_soup(next_url)
        # We couldn't get the next url.
        if soup is None:
            break

    return keys
