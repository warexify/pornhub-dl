#!/bin/env python3
"""A scraper for pornhub."""
import os
from datetime import datetime

from pornhub.db import get_session
from pornhub.logging import logger
from pornhub.helper import link_duplicate
from pornhub.models import User, Playlist, Clip, Channel
from pornhub.download import download_video
from pornhub.extractors import (
    get_channel_info,
    get_user_info,
    get_playlist_info,
    download_channel_videos,
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


def get_channel(args):
    """Get all information about the channel and download it's videos."""
    channel_id = args['id']
    session = get_session()

    channel = session.query(Channel).get(channel_id)
    if channel is None:
        info = get_channel_info(channel_id)
        channel = Channel.get_or_create(session, channel_id, info['name'])

    download_channel_videos(session, channel)
    channel.last_scan = datetime.now()
    session.commit()


def get_video(args):
    """Get a single videos."""
    session = get_session()

    folder = args.get('folder')

    clip = Clip.get_or_create(session, args['viewkey'])
    if clip.completed:
        if clip.title is not None and \
           clip.extension is not None:
            target_path = get_clip_path(folder, clip.title, clip.extension)
            link_duplicate(clip, target_path)

        logger.info("Clip already exists")
        return

    success, info = download_video(args['viewkey'], name=folder)

    clip.title = info['title']
    clip.tags = info['tags']
    clip.cartegories = info['categories']
    clip.completed = True
    clip.location = info['out_path']
    clip.extension = info['ext']

    session.commit()


def update(args):
    """Get all information about a user and download their videos."""
    session = get_session()

    users = session.query(User).order_by(User.key).all()
    for user in users:
        logger.info(f'\nStart downloading user: {user.name}')
        download_user_videos(session, user)
        user.last_scan = datetime.now()
        session.commit()

    playlists = session.query(Playlist).order_by(Playlist.name).all()
    for playlist in playlists:
        logger.info(f'\nStart downloading playlist: {playlist.name}')
        download_playlist_videos(session, playlist)
        user.last_scan = datetime.now()
        session.commit()

    channels = session.query(Channel).order_by(Channel.name).all()
    for channel in channels:
        logger.info(f'\nStart downloading channel: {channel.name}')
        download_channel_videos(session, channel)
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


def remove(args):
    """Get all information about a user and download their videos."""
    entity_type = args['type']
    key = args['key']

    session = get_session()
    if entity_type.lower() == 'user':
        user = session.query(User).get(key)
        session.delete(user)
    elif entity_type.lower() == 'playlist':
        playlist = session.query(Playlist).get(key)
        session.delete(playlist)
    elif entity_type.lower() == 'channel':
        channel = session.query(Channel).get(key)
        session.delete(channel)
    else:
        print(f"Unkown type {entity_type}. Use either `user`, `playlist` or `channel`")



    session.commit()
    print(f"{entity_type} {key} has been removed")
