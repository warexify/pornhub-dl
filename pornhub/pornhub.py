#!/bin/env python3
"""A scraper for pornhub."""
from datetime import datetime

from pornhub.db import get_session
from pornhub.models import User, Playlist
from pornhub.scraping import download_video
from pornhub.extractors import (
    get_user_info,
    get_playlist_info,
    download_user_videos,
    download_playlist_videos,
)


def get_user(args):
    """Get all information about a user and download their videos."""
    key = args['key']
    session = get_session()

    user = session.query(User).get(key)
    if user is None:
        info = get_user_info(key)
        user = User.get_or_create(session, key, info['name'], info['type'])

    user.subscribed = True
    session.commit()

    download_user_videos(session, user)
    session.last_scan = datetime.now()
    session.commit()


def get_playlist(args):
    """Get all information about the playlist and download it's videos."""
    playlist_id = args['id']
    session = get_session()

    playlist = session.query(Playlist).get(playlist_id)
    if playlist is None:
        info = get_playlist_info(playlist_id)
        playlist = Playlist.get_or_create(session, playlist_id, info['name'])

    download_playlist_videos(session, playlist)
    playlist.last_scan = datetime.now()
    session.commit()


def get_video(args):
    """Get a single videos."""
    session = get_session()

    url = f"https://www.pornhub.com/view_video.php?viewkey={args['viewkey']}"
    folder = args.get('folder')
    download_video(url, name=folder)

    session.commit()


def update(args):
    """Get all information about a user and download their videos."""
    session = get_session()
    users = session.query(User).all()
    playlists = session.query(Playlist).all()

    for user in users:
        print(f'\nStart downloading user: {user.name}')
        download_user_videos(session, user)
        user.last_scan = datetime.now()
        session.commit()

    for playlist in playlists:
        print(f'\nStart downloading playlist: {playlist.name}')
        download_playlist_videos(session, playlist)
        user.last_scan = datetime.now()
        session.commit()
