# Pornhub-dl

Download all videos of your favorite pornhub models, playlists and channels and update all your stuff with a simple command.

## Setup
You will need `poetry` for dependency management and venv creation: `poetry install --develop .`
The default config will create a new postgres database `pornhub`.
If you want to change this, you need to adjust the sqluri in `db.py`.

## Migrating

Just execute `poetry run alembic upgrade head`.
If you use another database engine/nam, you need to adjust the sqluri in alembic.ini as well.

## Usage
The project is used by invocing `runner.py`. In combination with poetry this looks like this: `poetry run python runner.py`  

There is a help for all commands, but here are some examples anyway:

`runner.py get_user [some_model]` Follow this user/model/pornstar and download all videos.  
`runner.py get_playlist [playlist_id]` Follow this user/model/pornstar and download all videos.  
`runner.py update` Get the newest videos of all your followed models and channels.  


## How does it work?

All videos are downloaded into respective folder with the name of the respective user.
Pornhub-dl uses youtube-dl as a download backend, but implements own functionality, such as custom user meta-data extraction, user/channel following, as well as video list extraction and retry logic for rate limiting.

Pornhub-dl crawls all video urls of all followed users/channels and remembers the ids of downloaded videos.
If you update your database, all new videos will be downloaded, while old ones are simply skipped without invoking youtube-dl.

## Files and Directories
Videos are downloaded to `~/pornhub/`. A sqlite database is created in `~/.local/share/pornhub.db`.

Disclaimer:

This project is not associated in any way with the operators of the official pornhub.com
It's just a small and fun side-project in reaction to the possibly imminent censorship in the EU.
