"""Helper for extracting meta information from pornhub."""
import re
import time
import requests
from bs4 import BeautifulSoup

from pornhub.models import User, Clip
from pornhub.scraping import get_soup, download_video


def download_user_videos(session, user):
    """Download all videos of a user."""
    viewkeys = get_user_video_viewkeys(user)
    secondary_viewkeys = get_secondary_user_video_viewkeys(user)
    viewkeys = set(viewkeys + secondary_viewkeys)

    print(f'Found {len(viewkeys)} videos.')
    for viewkey in viewkeys:
        clip = Clip.get_or_create(session, viewkey, user)

        # The clip has already been downloaded, skip it.
        if clip.completed and clip.user == user:
            continue

        url = f'https://www.pornhub.com/view_video.php?viewkey={viewkey}'

        success, info = download_video(url, user.name)
        if success:
            clip.title = info['title']
            clip.completed = True
            clip.user = user

            print(f'New video: {clip.title}')

        session.commit()


def get_user_video_url(user_type, key):
    """Compile the user videos url."""
    return f'https://www.pornhub.com/{user_type}/{key}/videos'


def get_secondary_user_video_url(user_type, key):
    """Check if there is a secondary video url."""
    possible_urls = [
        f'https://www.pornhub.com/{user_type}/{key}/videos/public',
        f'https://www.pornhub.com/{user_type}/{key}/videos/upload',
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
    name = get_name_from_soup(soup, 'user')

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
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return user_type, url, soup

    raise Exception(f"Couldn't detect type for user {key}")


def get_name_from_soup(soup, website_type):
    """Get the name of the user by website."""
    if website_type == 'channel':
        section = soup.find_all('section', {'class': 'channelsProfile'})[0]
        wrapper = section.find_all('div', {'class': 'bottomExtendedWrapper'})[0]
        h1 = wrapper.find_all('h1')[0]
        a = h1.find_all('a')[0]
        name = a.contents[0]

    elif website_type == 'user':
        div = soup.find_all('div', {'class': 'nameSubscribe'})[0]
        h1 = div.find_all('h1')[0]
        name = h1.contents[0]

    elif website_type == 'video':
        info = soup.find_all('div', {'class': 'video-detailed-info'})[0]
        wrap = info.find_all('div', {'class': 'usernameWrap'})[0]
        h1 = wrap.find_all('a')[0]
        name = h1.contents[0]

    return name


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
        next_url = url + f'?page={current_page}'

        time.sleep(4)
        soup = get_soup(next_url)
        # We couldn't get the next url.
        if soup is None:
            break

    return keys


def get_secondary_user_video_viewkeys(user):
    """Scrape all public viewkeys of the user's videos."""
    url = get_secondary_user_video_url(user.user_type, user.key)

    # Couldn't find a public/upload video site
    if url is None:
        return []

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
        wrapper = soup.find_all('div', {'class': 'videoUList'})[0]
        videos = wrapper.find_all('ul')[0]

        for video in videos.find_all('li'):
            keys.append(video['_vkey'])

        current_page += 1
        next_url = url + f'?page={current_page}'

        time.sleep(4)

        soup = get_soup(next_url)
        # We couldn't get the next url.
        if soup is None:
            break

    return keys
