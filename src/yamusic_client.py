from yandex_music import *
from yandex_music.exceptions import *
from misc import *

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import GdkPixbuf, GLib

import pathlib

WORK_DIR = str(pathlib.Path(__file__).parent.resolve())
CACHE_DIR = GLib.get_user_cache_dir() + "/yamusic"

import json
import os


class YamusicClient:
    def __init__(self, token=None):
        self.token = token
        if has_internet():
            self.client = Client(token=token).init()
        else:
            self.client = None

    def init_client(self):
        self.client = Client(token=self.token).init()

    def get_liked_playlist(self):
        title = "Понравившиеся"
        kind = -1
        owner_id = self.client.me.account.uid
        cover = f"{WORK_DIR}/data/liked_cover.png"

        return {
            "title": title,
            "kind": kind,
            "owner_id": owner_id,
            "cover": cover,
        }

    def get_user_playlists(self):
        raw_playlists = [playlist for playlist in self.client.users_playlists_list()]

        playlists = []
        for i in range(len(raw_playlists)):
            raw_playlist = raw_playlists[i]
            title = raw_playlist.title
            kind = raw_playlist.kind
            owner_id = raw_playlist.owner.uid

            try:
                raw_playlist.cover.download(f"{CACHE_DIR}/playlists_covers/{owner_id}_{kind}.png")
                cover = f"{CACHE_DIR}/playlists_covers/{owner_id}_{kind}.png"
            except TypeError:
                cover = f"{WORK_DIR}/data/empty_playlist_cover.png"

            playlist = {
                "title": title,
                "kind": kind,
                "owner_id": owner_id,
                "cover": cover,
            }
            playlists.append(playlist)

        return playlists

    def get_all_user_playlists(self, use_cache=True):
        if has_internet() and self.client:
            playlists = [self.get_liked_playlist()] + self.get_user_playlists()

            if use_cache:
                json.dump(playlists, open(f"{CACHE_DIR}/user_playlists.json", "w", encoding="utf-8"),
                          indent=4, sort_keys=True, ensure_ascii=False)

        elif os.path.exists(f"{CACHE_DIR}/user_playlists.json"):
            playlists = json.load(open(f"{CACHE_DIR}/user_playlists.json", "r"))
        else:
            playlists = []

        return playlists

    def get_track_url(self, track):
        while True:
            try:
                url = sorted(self.client.tracks_download_info(track.id, True),
                             key=lambda x: x["bitrate_in_kbps"],
                             reverse=True)[0].get_direct_link()
                return url
            except NetworkError:
                continue

    def fetch_tracks_from_playlist(self, playlist, use_cache=True):
        def cache_tracks(tracks_to_cache):
            if not tracks_to_cache:
                return

            if os.path.exists(f"{CACHE_DIR}/cached_tracks.json"):
                cache = json.load(open(f"{CACHE_DIR}/cached_tracks.json", "r", encoding="utf8"))
            else:
                cache = {}

            reformatted_tracks = [
                {
                    "title": track.title,
                    "artists": [artist.name for artist in track.artists],
                    "id": track.id,
                    "available": os.path.exists(f"{CACHE_DIR}/downloaded_tracks/{track.id}.mp3"),
                } for track in tracks_to_cache
            ]
            
            #del cache[f"{playlist['owner_id']}_{playlist['kind']}"]
            cache[f"{playlist['owner_id']}_{playlist['kind']}"] = reformatted_tracks

            json.dump(cache, open(f"{CACHE_DIR}/cached_tracks.json", "w", encoding="utf8"),
                      indent=4, sort_keys=True, ensure_ascii=False)

        tracks = []
        if has_internet() and self.client:
            while True:
                try:
                    if playlist["kind"] == -1:
                        short_tracks = self.client.users_likes_tracks()
                        short_tracks_ids = [short_track.id for short_track in short_tracks]
                        tracks = self.client.tracks(short_tracks_ids)
                    else:
                        full_playlist = self.client.playlists_list(f"{playlist['owner_id']}:{playlist['kind']}")[0]
                        short_tracks = full_playlist.fetch_tracks()
                        tracks = [short_track.track for short_track in short_tracks]
                except NetworkError:
                    continue
                break

            if use_cache:
                cache_tracks(tracks)
        elif os.path.exists(f"{CACHE_DIR}/cached_tracks.json"):
            tracks = json.load(open(f"{CACHE_DIR}/cached_tracks.json", "r", encoding="utf8"))[f"{playlist['owner_id']}_{playlist['kind']}"]
            for track in tracks:
                del track["available"]
                track["available"] = os.path.exists(f"{CACHE_DIR}/downloaded_tracks/{track['id']}.mp3")
        else:
            tracks = []

        return tracks

    def download_track_cover(self, track, download_path=f"{CACHE_DIR}/tracks_covers"):
        if has_internet() and self.client is not None:
            try:
                track.download_cover(f"{download_path}/{track.id}.png")
                cover = GdkPixbuf.Pixbuf.new_from_file(f"{download_path}/{track.id}.png")
                return cover
            except AttributeError:
                cover = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 50, 50)
                cover.fill(0x000000ff)
                return cover
        else:
            cover = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 50, 50)
            cover.fill(0x000000ff)
            return cover
