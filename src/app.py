import random

import yandex_music

from yamusic_client import *
from audio_player import *
from misc import *

from ui.yamusic_window import YamusicWindow
from ui.track_widget import TrackWidget
from ui.playlist_widget import PlaylistWidget

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio, GLib

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class YamusicApp(Adw.Application):
    def __init__(self, token, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.token = token

        self.window: YamusicWindow = None
        self.audio_player: AudioPlayer = None
        self.client: YamusicClient = None

        # Music params
        self.track_volume = 1
        self.track_position = 0
        self.track_duration = 0
        self.current_track_index = 0

        self.playing_state = AudioState.null

        self.tracks_queue = []
        self.shuffled_indexes = []

        self.current_track_widget: TrackWidget = None
        self.current_playlist_widget = None
        self.current_playing_playlist_widget = None
        self.track_positioning_timeout = None
        self.setting_tracks_queue = None

        self.already_setting_track = False
        self.shuffle = False

        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.window = YamusicWindow(application=app)
        self.window.present()

        self.audio_player = AudioPlayer()
        self.audio_player.set_volume(self.track_volume)

        self.client = YamusicClient(token=self.token)

        # Connecting Signals
        self.window.player_controls_frame.prev_track_button.connect("clicked", self._on_prev_track_btn_clicked)
        self.window.player_controls_frame.next_track_button.connect("clicked", self._on_next_track_btn_clicked)
        self.window.player_controls_frame.play_track_button.connect("clicked", self._on_play_track_btn_clicked)
        self.window.player_controls_frame.show_queue_button.connect("clicked", self._on_show_queue_btn_clicked)
        self.window.player_controls_frame.shuffle_playlist_button.connect("clicked", self._on_shuffle_btn_clicked)
        self.window.player_controls_frame.download_track_button.connect("clicked", self._on_download_track_btn_clicked)
        self.window.player_controls_frame.track_volume_button.connect("clicked",
                                                                      lambda btn: self.window.player_controls_frame
                                                                      .volume_popover.show())

        self.window.player_controls_frame.track_slider.connect("change-value", self._on_slider_moved)
        self.window.player_controls_frame.volume_slider.connect("value-changed", self._on_volume_slider_moved)
        self.window.player_controls_frame.track_volume_button_gesture.connect("scroll", self._on_volume_bnt_scrolled)

        self.window.header_library_button.connect("clicked", self._on_library_btn_clicked)
        self.window.header_main_page_button.connect("clicked", self._on_main_page_btn_clicked)

        self.window.library.connect("playlist-clicked", self._on_playlist_clicked)
        self.window.library.connect("track-clicked", self._on_track_clicked)

        self._on_library_btn_clicked(self.window.header_library_button)

        self.window.library.play_playlist_button.connect("clicked", self._on_play_playlist_btn_clicked)
        self.window.library.search_track_line.connect("search-changed", self._search_in_playlist_changed)

        GLib.timeout_add(100, self.update_timer)
        GLib.timeout_add_seconds(1, self.sync_timer)
        GLib.timeout_add_seconds(1, self.sync_slider)

    def update_timer(self):
        if self.setting_tracks_queue and not self.already_setting_track:
            new_track, new_track_widget = self.setting_tracks_queue
            self.create_track_setting_job(new_track, new_track_widget)
            self.setting_tracks_queue = None

        if self.playing_state is AudioState.playing and self.audio_player.state is AudioState.null:
            self.audio_player.stop()
            self.set_next_track()
            return True

        if not (self.playing_state is AudioState.playing and self.audio_player.state is AudioState.playing):
            return True

        # Sync the slider range according to the track duration
        if self.audio_player.duration:
            if self.window.player_controls_frame.track_slider.get_adjustment().get_upper() != self.track_duration:
                self.track_duration = self.audio_player.duration
                self.window.player_controls_frame.track_slider.set_range(0, self.track_duration)
            if self.track_duration != self.audio_player.duration:
                self.track_duration = self.audio_player.duration

        return True

    def sync_slider(self):
        # Moving the slider position according to the track position
        if (diff := self.audio_player.position - self.track_position) > 500:
            self.track_position += diff
            self.window.player_controls_frame.track_slider.set_value(self.track_position)
        elif diff < 0:
            self.track_position = self.audio_player.position
            self.window.player_controls_frame.track_slider.set_value(self.track_position)

        return True

    # A function that synchronizes the timer label according to the track position
    def sync_timer(self):
        # A function that makes time a little more beautiful =)
        def beautify_time(seconds):
            if seconds < 60:
                seconds = str(round(seconds))
                if len(seconds) < 2:
                    seconds = f"0{seconds}"
                return f"00:{seconds}"

            minutes = int(seconds // 60)
            seconds = int(seconds - minutes * 60)

            minutes = str(minutes)
            seconds = str(seconds)

            if len(minutes) < 2:
                minutes = f"0{minutes}"
            if len(seconds) < 2:
                seconds = f"0{seconds}"

            return f"{minutes}:{seconds}"

        # Getting the elapsed time and duration in seconds
        elapsed_time = self.track_position // 1000
        duration = self.track_duration // 1000

        # Abracadabra! Now the values are pretty!
        elapsed_time = beautify_time(elapsed_time)
        duration = beautify_time(duration)

        self.window.player_controls_frame.track_timer.set_label(f"\n{elapsed_time}/{duration}")

        return True

    def _on_prev_track_btn_clicked(self, _btn):
        self.set_prev_track()

    def set_prev_track(self):
        if self.current_track_index <= 0:
            if self.audio_player.state is AudioState.null:
                self.current_track_widget.playing_animation.stop()
                self.window.player_controls_frame.play_track_button.set_child(
                    Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-playback-start-symbolic")))
            return

        self.current_track_index -= 1

        if self.shuffle:
            new_track_widget: TrackWidget = self.window.library.tracks_widgets.copy().pop(
                self.shuffled_indexes[self.current_track_index])
        else:
            new_track_widget = self.window.library.tracks_widgets.copy().pop(self.current_track_index)

        if not new_track_widget.track_available:
            self.set_prev_track()
            return

        new_track = new_track_widget.track

        if self.already_setting_track:
            self.setting_tracks_queue = (new_track, new_track_widget)
        else:
            self.create_track_setting_job(new_track, new_track_widget)

    def _on_next_track_btn_clicked(self, _btn):
        self.set_next_track()

    def set_next_track(self):
        if self.current_track_index >= len(self.tracks_queue) - 1:
            if self.audio_player.state is AudioState.null:
                self.current_track_widget.playing_animation.stop()
                self.window.player_controls_frame.play_track_button.set_child(
                    Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-playback-start-symbolic")))
            return

        self.current_track_index += 1

        if self.shuffle:
            new_track_widget: TrackWidget = self.window.library.tracks_widgets.copy().pop(
                self.shuffled_indexes[self.current_track_index])
        else:
            new_track_widget = self.window.library.tracks_widgets.copy().pop(self.current_track_index)

        if not new_track_widget.track_available:
            self.set_prev_track()
            return

        new_track = new_track_widget.track

        if self.already_setting_track:
            self.setting_tracks_queue = (new_track, new_track_widget)
        else:
            self.create_track_setting_job(new_track, new_track_widget)

    def _on_play_track_btn_clicked(self, _btn):
        if self.playing_state is AudioState.playing:
            self.playing_state = AudioState.paused
            self.audio_player.pause()

            self.window.player_controls_frame.play_track_button.set_child(
                Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-playback-start-symbolic")))

            if self.current_track_widget:
                self.current_track_widget.playing_animation.pause()

        elif self.playing_state is AudioState.paused:
            self.playing_state = AudioState.playing
            self.audio_player.play()

            self.window.player_controls_frame.play_track_button.set_child(
                Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-playback-pause-symbolic")))

            if self.current_track_widget:
                self.current_track_widget.playing_animation.play()

    def _on_show_queue_btn_clicked(self, _btn):
        if not self.tracks_queue:
            return

        title = self.current_playing_playlist_widget.playlist["title"]
        self.window.library.playlist_info_label.set_markup(f"<sup><i>Плейлист пользователя</i></sup>\n"
                                                           f"<b>{title}</b>")

        self.window.library.clear_tracks()
        self.window.library.tracks_widgets = self.tracks_queue
        self.window.library.redraw_tracks_widgets()

    def _on_shuffle_btn_clicked(self, _btn):
        if self.shuffle:
            self.shuffle = False
            self.current_track_index = self.shuffled_indexes[self.current_track_index]

            self.window.player_controls_frame.shuffle_playlist_button.get_style_context().remove_class(
                "suggested-action")

        else:
            self.shuffle = True
            self.shuffle_queue()

            self.window.player_controls_frame.shuffle_playlist_button.get_style_context().add_class("suggested-action")

    def shuffle_queue(self):
        if not self.tracks_queue:
            return

        self.shuffled_indexes = list(range(0, len(self.tracks_queue)))
        random.shuffle(self.shuffled_indexes)

        if self.current_track_index:
            self.shuffled_indexes.remove(self.current_track_index)
            self.shuffled_indexes = [self.current_track_index] + self.shuffled_indexes
            self.current_track_index = 0

    def _on_download_track_btn_clicked(self, _btn):
        track_downloaded = os.path.exists(f"{CACHE_DIR}/downloaded_tracks/{self.current_track_widget.track_id}.mp3")
        task = Gio.Task.new(self, Gio.Cancellable.new(), None)

        if track_downloaded:
            GLib.idle_add(task.run_in_thread, lambda *args: self.remove_track(self.current_track_widget))
        else:
            GLib.idle_add(task.run_in_thread, lambda *args: self.download_track(self.current_track_widget))

    def download_track(self, track_widget):
        track_widget.downloading_spinner.start()

        downloading_spinner = Gtk.Spinner()
        if self.current_track_widget == track_widget:
            self.window.player_controls_frame.download_track_button.set_child(downloading_spinner)
            downloading_spinner.start()

        track: yandex_music.Track = track_widget.track
        track.download(f"{CACHE_DIR}/downloaded_tracks/{track_widget.track_id}.mp3")

        track_widget.downloading_spinner.stop()
        downloading_spinner.stop()
        if self.current_track_widget == track_widget:
            self.window.player_controls_frame.download_track_button.set_child(
                Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("emblem-ok-symbolic")))

    def remove_track(self, track_widget):
        removing_spinner = Gtk.Spinner()
        if self.current_track_widget == track_widget:
            self.window.player_controls_frame.download_track_button.set_child(removing_spinner)
            removing_spinner.start()

        os.remove(f"{CACHE_DIR}/downloaded_tracks/{track_widget.track_id}.mp3")

        removing_spinner.stop()
        if self.current_track_widget == track_widget:
            self.window.player_controls_frame.download_track_button.set_child(
                Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("folder-download-symbolic")))

    def _on_slider_moved(self, _widget, _enum, value):
        # self.track_position = round(value)
        # self.audio_player.set_position(self.track_position)
        self.track_position = value
        self.sync_timer()
        #
        if self.track_positioning_timeout is not None:
            GLib.source_remove(self.track_positioning_timeout)
        self.track_positioning_timeout = GLib.timeout_add(100, lambda: self.change_track_position(value))

    # This function is needed because Gtk.Scale for some reason does not trigger the "released" event =\
    def change_track_position(self, value):
        self.audio_player.set_position(value)
        self.track_positioning_timeout = None

    def _on_volume_slider_moved(self, slider: Gtk.Scale):
        volume = slider.get_value() / 100
        self.change_volume(
            volume)  # self.track_volume = slider.get_value() / 100  # self.audio_player.set_volume(self.track_volume)

    def _on_volume_bnt_scrolled(self, _controller, _dx, dy):
        if 0 <= self.track_volume - dy / 8 <= 1:
            volume = self.track_volume - dy / 8
            self.window.player_controls_frame.volume_slider.set_value(volume * 100)
            self.change_volume(volume)  # self.audio_player.set_volume(self.track_volume)

    def change_volume(self, volume):
        self.track_volume = volume
        self.audio_player.set_volume(self.track_volume)

        if volume == 0:
            self.window.player_controls_frame.track_volume_button.set_child(
                Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("audio-volume-muted-symbolic")))
        elif 0 < volume <= 0.3:
            self.window.player_controls_frame.track_volume_button.set_child(
                Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("audio-volume-low-symbolic")))
        elif 0.3 < volume <= 0.7:
            self.window.player_controls_frame.track_volume_button.set_child(
                Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("audio-volume-medium-symbolic")))
        else:
            self.window.player_controls_frame.track_volume_button.set_child(
                Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("audio-volume-high-symbolic")))

    def _on_library_btn_clicked(self, _btn):
        task = Gio.Task.new(self, Gio.Cancellable.new(), None)
        GLib.idle_add(task.run_in_thread, lambda *_args: self.load_library())

    def load_library(self):
        self.window.header_spinner.start()

        playlists = self.client.get_all_user_playlists()

        self.window.library.clear_playlists()

        for playlists in playlists:
            self.window.library.add_playlist(playlists)
        self.window.library.redraw_playlists_widgets()

        self.window.header_spinner.stop()

    def _on_main_page_btn_clicked(self, _btn):
        task = Gio.Task.new(self, Gio.Cancellable.new(), None)
        GLib.idle_add(task.run_in_thread, self.load_main_page)

    def load_main_page(self):
        pass

    def _on_playlist_clicked(self, library, playlist_widget: PlaylistWidget):
        self.current_playlist_widget = playlist_widget
        library.clear_tracks()

        playlist = playlist_widget.playlist

        playlist_title = playlist["title"]
        self.window.library.playlist_info_label.set_markup(f"<sup><i>Плейлист пользователя</i></sup>\n"
                                                           f"<b>{playlist_title}</b>")
        self.window.library.playlist_info_frame.show()

        task = Gio.Task.new(self, Gio.Cancellable.new(), None)
        GLib.idle_add(task.run_in_thread, lambda *_args: self.load_playlist(playlist))

    def load_playlist(self, playlist):
        self.window.header_spinner.start()

        tracks = self.client.fetch_tracks_from_playlist(playlist)

        for track in tracks:
            track_id = track.id if hasattr(track, "id") else track["id"]

            if hasattr(track, "title") and track.title is None:
                continue
            elif type(track) is dict and track["title"] is None:
                continue

            if self.current_track_widget and self.current_track_widget.track_id == track_id:
                self.window.library.tracks_widgets.append(self.current_track_widget)
                self.window.library.tracks_widgets[-1].track_number_label.set_text(
                    str(len(self.window.library.tracks_widgets)))
            elif widget := [widget for widget in self.tracks_queue if widget.track_id == track_id]:
                self.window.library.tracks_widgets.append(widget[0])
                self.window.library.tracks_widgets[-1].track_number_label.set_text(
                    str(len(self.window.library.tracks_widgets)))
            else:
                self.window.library.add_track(track)

        self.window.library.redraw_tracks_widgets()
        self.window.header_spinner.stop()

    def _on_track_clicked(self, library, track_widget):
        self.current_track_index = library.tracks_widgets.index(track_widget)
        self.tracks_queue = library.tracks_widgets
        self.current_playing_playlist_widget = self.current_playlist_widget

        if self.shuffle:
            self.shuffle_queue()

        track = track_widget.track

        if self.already_setting_track:
            self.setting_tracks_queue = (track, track_widget)
        else:
            self.create_track_setting_job(track, track_widget)

    def create_track_setting_job(self, track, track_widget):
        self.already_setting_track = True
        task = Gio.Task.new(self, Gio.Cancellable.new(), None)
        GLib.idle_add(task.run_in_thread, lambda *_args: self.set_track(track, track_widget))

    def set_track(self, track, track_widget, force_play=True):
        if not track_widget.track_available:
            self.set_next_track()
            return False

        self.window.header_spinner.start()

        was_playing = self.playing_state is AudioState.playing

        if self.current_track_widget:
            self.current_track_widget.playing_animation.stop()

        self.current_track_widget = track_widget
        self.playing_state = AudioState.null
        self.audio_player.stop()

        title = track_widget.title
        artists = track_widget.artists
        duration_ms = track_widget.duration_ms if track_widget.duration_ms else track.duration_ms

        self.window.player_controls_frame.track_title_label.set_text(f"{title}\n{artists}")
        self.track_position = 0
        self.track_duration = 0

        self.sync_timer()
        self.sync_slider()

        self.window.player_controls_frame.track_slider.set_value(0)
        self.window.player_controls_frame.track_slider.set_range(0, duration_ms)

        if os.path.exists(f"{CACHE_DIR}/downloaded_tracks/{track_widget.track_id}.mp3"):
            self.window.player_controls_frame.download_track_button.set_child(
                Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("emblem-ok-symbolic")))
        else:
            self.window.player_controls_frame.download_track_button.set_child(
                Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("folder-download-symbolic")))

        if has_internet() and self.client.client:
            url = self.client.get_track_url(track)
            self.audio_player.load_from_url(url)
        else:
            filepath = f"{CACHE_DIR}/downloaded_tracks/{track_widget.track_id}.mp3"
            self.audio_player.load_from_file(filepath)

        self.playing_state = AudioState.paused
        if was_playing or force_play:
            self._on_play_track_btn_clicked(self.window.player_controls_frame.play_track_button)

        track_cover = self.client.download_track_cover(track)
        self.window.player_controls_frame.track_cover_img.unparent()
        self.window.player_controls_frame.track_cover_img = Gtk.Image.new_from_pixbuf(track_cover)
        self.window.player_controls_frame.track_cover_img.set_vexpand(True)
        self.window.player_controls_frame.track_cover_img.set_size_request(30, 30)
        self.window.player_controls_frame.track_cover_img.set_margin_top(10)
        self.window.player_controls_frame.track_cover_img.set_margin_start(10)
        self.window.player_controls_frame.player_controls_grid.attach(
            self.window.player_controls_frame.track_cover_img, 0, 0, 1, 1)

        self.window.header_spinner.stop()

        self.already_setting_track = False

    def _on_play_playlist_btn_clicked(self, _btn):
        self.set_playlist(self.current_playlist_widget)

    def set_playlist(self, playlist_widget: PlaylistWidget):
        if self.current_track_widget:
            self.current_track_widget.playing_animation.stop()
        self.current_track_index = 0
        self.current_track_widget = 0
        self.current_playing_playlist_widget = playlist_widget
        self.tracks_queue = self.window.library.tracks_widgets.copy()

        if self.shuffle:
            self.shuffle_queue()
            new_track_widget = self.window.library.tracks_widgets[self.shuffled_indexes[self.current_track_index]]
            new_track = new_track_widget.track
        else:
            new_track_widget = self.window.library.tracks_widgets[self.current_track_index]
            new_track = new_track_widget.track

        task = Gio.Task.new(self, Gio.Cancellable.new(), None)
        GLib.idle_add(task.run_in_thread, lambda *_args: self.set_track(new_track, new_track_widget))

    def _search_in_playlist_changed(self, entry):
        search_request = entry.get_text().lower()
        self.search_track_in_playlist(search_request)

    def search_track_in_playlist(self, search_request):
        for track_widget in self.window.library.tracks_widgets:
            track_widget.playing_animation.stop()

            if search_request in track_widget.title.lower() or search_request in track_widget.artists.lower():
                track_widget.set_visible(True)

                # if track_widget == self.current_track_widget:

                    # track_widget.playing_animation.play()

                continue

            track_widget.set_visible(False)
            track_widget.playing_animation.stop()
