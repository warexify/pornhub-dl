"""Playlist extracting logic."""
import re
import os
import requests
from bs4 import BeautifulSoup

from pornhub.models import Clip
from pornhub.logging import logger
from pornhub.helper import get_clip_path, link_duplicate
from pornhub.download import get_soup, download_video


def download_playlist_videos(session, playlist):
    """Download all videos of a playlist."""
    viewkeys = get_playlist_video_viewkeys(playlist)

    full_success = True

    logger.info(f'Found {len(viewkeys)} videos.')
    for viewkey in viewkeys:
        clip = Clip.get_or_create(session, viewkey)

        # The clip has already been downloaded, skip it.
        if clip.completed:
            if clip.title is not None and \
               clip.extension is not None:
                target_path = get_clip_path(playlist.name, clip.title, clip.extension)
                link_duplicate(clip, target_path)

            continue

        success, info = download_video(viewkey, f'playlists/{playlist.name}')
        if success:
            clip.title = info['title']
            clip.tags = info['tags']
            clip.cartegories = info['categories']
            clip.completed = True
            clip.location = info['out_path']
            clip.extension = info['ext']

            logger.info(f'New video: {clip.title}')
        else:
            full_success = False

        session.commit()
        time.sleep(20)

    return full_success

def get_playlist_video_url(playlist_id):
    """Compile the user videos url."""
    is_premium = os.path.exists('http_cookie_file')
    if is_premium:
        return f'https://www.pornhubpremium.com/playlist/{playlist_id}'

    return f'https://www.pornhub.com/playlist/{playlist_id}'


def get_playlist_info(playlist_id):
    """Get meta information from playlist website."""
    url = get_playlist_video_url(playlist_id)
    soup = get_soup(url)
    if soup is None:
        logger.error("Got invalid response for playlist: {url}")
        sys.exit(1)

    header = soup.find(id='playlistTopHeader')
    if header is None:
        logger.info(f"Couldn't get info for playlist: {url}")
        check_logged_out(soup)
        sys.exit(1)

    link = header.find_all('a')[0]

    name = link.text.strip()
    name = name.replace(' ', '_')
    name = re.sub(r'[\W]+', '_', name)

    return {
        'name': name,
    }


def get_playlist_video_viewkeys(playlist):
    """Scrape all viewkeys of the playlist's videos."""
    url = get_playlist_video_url(playlist.id)
    soup = get_soup(url)
    if soup is None:
        logger.error(f"Couldn't find site for playlist {playlist.id}")
        sys.exit(1)

    videos = soup.find(id='videoPlaylist')

    keys = []
    for video in videos.find_all('li'):
        # Only get entries with _vkey attribute
        # There exist some elements, which have programmatic purpose
        if video.has_attr('_vkey'):
            keys.append(video['_vkey'])

    return keys
