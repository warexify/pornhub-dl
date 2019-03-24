#!/bin/env python3
"""A scraper for pornhub."""
from datetime import datetime
from pornhub.scraping import (
    get_user_video_viewkeys,
    download_video,
)
from pornhub.db import get_session
from pornhub.helper import get_user_info
from pornhub.models import User, Clip


def create_user(args):
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


def download_user_videos(session, user):
    """Download all videos of a user."""
    viewkeys = get_user_video_viewkeys(user)
    print(f'Found {len(viewkeys)} videos.')
    for viewkey in viewkeys:
        clip = Clip.get_or_create(session, viewkey, user)

        # The clip has already been downloaded, skip it.
        if clip.completed:
            continue

        url = f'https://www.pornhub.com/view_video.php?viewkey={viewkey}'

        info = download_video(url, user.name)
        clip.title = info['title']
        clip.completed = True

        print(f'New video: {clip.title}')

        session.commit()


def update(args):
    """Get all information about a user and download their videos."""
    session = get_session()
    users = session.query(User).all()

    for user in users:
        download_user_videos(session, user)
        user.last_scan = datetime.now()
        session.commit()


def get_video(args):
    """Download a single video."""
    return
