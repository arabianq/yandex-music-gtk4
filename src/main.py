from app import *
from misc import *
from oauth import *

import os


if __name__ == "__main__":
    dirs = [CACHE_DIR, f"{CACHE_DIR}/playlists_covers", f"{CACHE_DIR}/tracks_covers", f"{CACHE_DIR}/downloaded_tracks"]

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
