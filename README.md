# Pornhub-dl

Download all videos of your favorite pornhub models, playlists and channels and update all your stuff with a simple command.

## Setup
1. You will need `poetry` for dependency management and venv creation: `poetry install --develop .`
2. The default config will create a new postgres database `pornhub` when first running the program.
Make sure your user has proper rights.
If you want to change this, you need to adjust the sqluri in `db.py`.

3. If you want to be up to date with migrations, set the alembic head to your current version.
You can use this by utilizing `potry run alembic history` and `poetry run alembic stamp $stamp`


## Migrating

Just execute `poetry run alembic upgrade head`.
If you use another database engine/nam, you need to adjust the sqluri in alembic.ini as well.

## Usage
The project is used by invocing `pornhub_dl.py`. In combination with poetry this looks like this: `poetry run python runner.py`  

There is a help for all commands, but here are some examples anyway:

`pornhub_dl.py user [some_model]` Follow this user/model/pornstar and download all videos.  
`pornhub_dl.py playlist [playlist_id]` Follow this user/model/pornstar and download all videos.  
`pornhub_dl.py video [vkey]` Download a single video by viewkey e.g. `ph56e961d32ce26`.  
`pornhub_dl.py update` Get the newest videos of all your followed models and channels.  


## How does it work?

All videos are downloaded into respective folder with the name of the respective user.
Pornhub-dl uses youtube-dl as a download backend, but implements own functionality, such as custom user meta-data extraction, user/channel following, as well as video list extraction and retry logic for rate limiting.

Pornhub-dl crawls all video urls of all followed users/channels and remembers the ids of downloaded videos.
If you update your database, all new videos will be downloaded, while old ones are simply skipped without invoking youtube-dl.

## Configuration
When starting the downloader for the first time, a configuration file is created at `~/.config/pornhub_dl.toml`


- `location`: Video download location. Default: `~/pornhub/`
- `sql_uri`: Your sql location. Default: `'postgres://localhost/pollbot'`

Disclaimer:
This project is not associated in any way with the operators of the official pornhub.com
It's just a small and fun side-project in reaction to the possibly imminent censorship in the EU.


## Premium

To enable premium, copy your Pornhub cookies and paste them to `./cookie_file`.
The cookies file must be formatted after the `Netscape cookie file format`.
The cookie file can be, for instance, created with his tool:

https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/


On top of that, create a second file `http_cookie_file`
Simply copy the `Cookie` header of any logged in pornhub premium domain request.
Those can be extracted using your browser's network debugging tool.
