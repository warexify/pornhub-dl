"""Helper for extracting meta information from pornhub."""
import requests
from bs4 import BeautifulSoup

from pornhub.models import User


def get_user_video_url(user_type, key):
    """Compile the user videos url."""
    return f'https://www.pornhub.com/{user_type}/{key}/videos'


def get_user_info(key):
    """Get all necessary user information."""
    user_type, url, soup = get_user_type_and_url(key)
    name = get_name_from_soup(soup, 'user')

    return {
        'type': user_type,
        'url': url,
        'name': name.strip(),
    }


def get_user_type_and_url(key):
    """Detect the user type and the respective url for this user."""
    possible_urls = {}
    for user_type in [User.USER, User.MODEL, User.PORNSTAR]:
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
