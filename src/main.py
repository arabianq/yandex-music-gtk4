from app import *
from oauth import *

import os
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import GLib

GLib.threads_init()

import pathlib

WORK_DIR = str(pathlib.Path(__file__).parent.resolve())
CACHE_DIR = GLib.get_user_cache_dir() + "/yamusic"


if __name__ == "__main__":
    dirs = [
        CACHE_DIR, f"{CACHE_DIR}/playlists_covers", f"{CACHE_DIR}/tracks_covers",
        f"{CACHE_DIR}/downloaded_tracks"
    ]

    for directory in dirs:
        if not os.path.exists(directory):
            os.mkdir(directory)  

    if not os.path.exists(f"{CACHE_DIR}/token"):
        token = oauth()

        if not token:
            exit()

        open(f"{CACHE_DIR}/token", "w", encoding="utf-8").write(token)

    else:
        token = open(f"{CACHE_DIR}/token", "r", encoding="utf-8").read()

        if not token:
            os.remove(f"{CACHE_DIR}/token")
            exit()

    application = YamusicApp(token=token, application_id="com.arabian.yamusic")
    application.run()
