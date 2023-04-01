import urllib3
from urllib3.exceptions import MaxRetryError

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import GLib

import pathlib


WORK_DIR = str(pathlib.Path(__file__).parent.resolve())
CACHE_DIR = GLib.get_user_cache_dir() + "/yamusic"


def has_internet():
    try:
        urllib3.PoolManager().request("GET", "https://music.yandex.ru")
    except MaxRetryError:
        return False
    return True
