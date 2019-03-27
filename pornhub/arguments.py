"""Commandline argument handling."""
import argparse
from pornhub.pornhub import update, create_user, get_video, create_playlist

parser = argparse.ArgumentParser(description='Download your favorite pornhub stuff.')

# Initialize supbparser
subparsers = parser.add_subparsers(
    title='Pornhub download functionality',
    description='Download all the porn',
)

# Get a specific video
get_video_sp = subparsers.add_parser('video', help='Get a single pornhub video.')
get_video_sp.add_argument('viewkey', type=str, help='The viewkey of the video (e.g ph5c8a344233560.')
get_video_sp.set_defaults(func=get_video)

# Get all videos from a user
get_user_sp = subparsers.add_parser('get_user', help='Get all videos from a user.')
get_user_sp.add_argument(
    'key', type=str, help='The key of the user you want to download (name in url e.g. /model/lure-lady).')
get_user_sp.set_defaults(func=create_user)

# Get all videos from a playlist
get_playlist_sp = subparsers.add_parser('get_playlist', help='Get all videos from a playlist.')
get_playlist_sp.add_argument(
    'id', type=str, help='The id of the playlist you want to download (number in url e.g. /playlists/51023901).')
get_playlist_sp.set_defaults(func=create_playlist)


# Get new videos of all subscribed users/channels
update_sp = subparsers.add_parser('update', help='Get new videos of all subscribed users/channels.')
update_sp.set_defaults(func=update)
