"""Playlist extracting logic."""
import requests
from bs4 import BeautifulSoup

from pornhub.scraping import get_soup, download_video
from pornhub.models import Clip


def download_playlist_videos(session, playlist):
    """Download all videos of a playlist."""
    viewkeys = get_playlist_video_viewkeys(playlist)
    print(f'Found {len(viewkeys)} videos.')
    for viewkey in viewkeys:
        clip = Clip.get_or_create(session, viewkey, playlist)

        # The clip has already been downloaded, skip it.
        if clip.completed:
            continue

        url = f'https://www.pornhub.com/view_video.php?viewkey={viewkey}'

        success, info = download_video(url, f'playlists/{playlist.name}')
        if success:
            clip.title = info['title']
            clip.completed = True

            print(f'New video: {clip.title}')

        session.commit()


def get_playlist_video_url(playlist_id):
    """Compile the user videos url."""
    return f'https://www.pornhub.com/playlist/{playlist_id}'


def get_playlist_info(playlist_id):
    """Get meta information from playlist website."""
    url = get_playlist_video_url(playlist_id)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        raise Exception("Got invalid response for playlist")

    header = soup.find_all('div', {'id': 'playlistTopHeader'})[0]
    link = header.find_all('a')[0]

    return {
        'name': link.text,
    }


def get_playlist_video_viewkeys(playlist):
    """Scrape all viewkeys of the playlist's videos."""
    url = f'https://www.pornhub.com/playlist/{playlist.id}'
    soup = get_soup(url)

    videos = soup.find_all('ul', {'id': 'videoPlaylist'})[0]

    keys = []
    for video in videos.find_all('li'):
        keys.append(video['_vkey'])

    return keys
