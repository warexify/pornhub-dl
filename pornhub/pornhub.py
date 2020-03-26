#!/bin/env python3
"""A scraper for pornhub."""
import os
from datetime import datetime

from pornhub.db import get_session
from pornhub.models import User, Playlist, Clip
from pornhub.download import download_video
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

    folder = args.get('folder')
    success, info = download_video(args['viewkey'], name=folder)

    if success:
        print(info)

    session.commit()


def update(args):
    """Get all information about a user and download their videos."""
    session = get_session()
    users = session.query(User).all()

    for user in users:
        print(f'\nStart downloading user: {user.name}')
        download_user_videos(session, user)
        user.last_scan = datetime.now()
        session.commit()

    playlists = session.query(Playlist).all()
    for playlist in playlists:
        print(f'\nStart downloading playlist: {playlist.name}')
        download_playlist_videos(session, playlist)
        user.last_scan = datetime.now()
        session.commit()

    clips = (
        session.query(Clip)
            .filter(Clip.completed.is_(False))
            .filter(Clip.location.isnot(None))
            .all()
    )

    for clip in clips:
        download_video(clip.viewkey, name=os.path.dirname(clip.location))
        clip.completed = True
        session.commit()


def reset(args):
    """Get all information about a user and download their videos."""
    session = get_session()
    session.query(Clip).update({"completed": False})
    session.commit()

    print("All videos have been scheduled for new download. Please run `update` to start downloading.")
