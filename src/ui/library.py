from src.ui.playlist_widget import PlaylistWidget
from src.ui.track_widget import TrackWidget

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject


class Library(Gtk.Grid):

    library_flag = True

    __gsignals__ = {"playlist-clicked": (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)),
                    "track-clicked": (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)), }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_column_homogeneous(True)

        self.set_column_spacing(5)
        self.set_margin_start(5)
        self.set_margin_end(5)
        self.set_margin_top(5)
        self.set_margin_bottom(5)

        self.users_playlists_frame = Gtk.Frame()
        self.users_playlists_frame.set_hexpand(True)
        self.users_playlists_frame.set_vexpand(True)
        self.attach(self.users_playlists_frame, 0, 0, 1, 1)

        self.users_playlists_scrolled = Gtk.ScrolledWindow()
        self.users_playlists_scrolled.set_hexpand(True)
        self.users_playlists_scrolled.set_vexpand(True)
        self.users_playlists_frame.set_child(self.users_playlists_scrolled)

        self.users_playlists_box = Gtk.FlowBox(orientation=Gtk.Orientation.HORIZONTAL)
        self.users_playlists_box.set_valign(Gtk.Align.START)
        self.users_playlists_box.set_column_spacing(3)
        self.users_playlists_box.set_row_spacing(3)
        self.users_playlists_box.set_margin_start(5)
        self.users_playlists_box.set_margin_end(5)
        self.users_playlists_box.set_margin_top(5)
        self.users_playlists_box.set_margin_bottom(5)
        self.users_playlists_scrolled.set_child(self.users_playlists_box)

        # self.create_playlist_button = Gtk.Button()
        # self.create_playlist_button.set_icon_name("list-add-symbolic")
        # img = Gtk.Image.new_from_file(f"{WORK_DIR}/data/add_icon.svg")
        # img.set_margin_start(5)
        # img.set_margin_end(5)
        # img.set_margin_top(5)
        # img.set_margin_bottom(5)
        # img.set_valign(Gtk.Align.START)
        # img.set_halign(Gtk.Align.CENTER)
        # img.set_size_request(100, 100)
        # self.create_playlist_button.set_child(img)
        # self.create_playlist_button.set_has_frame(False)
        # self.users_playlists_box.append(self.create_playlist_button)

        self.playlist_displayed_frame = Gtk.Frame()
        self.playlist_displayed_frame.set_vexpand(True)
        self.attach(self.playlist_displayed_frame, 1, 0, 1, 1)

        self.playlist_displayed_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.playlist_displayed_box.set_hexpand(True)
        self.playlist_displayed_box.set_vexpand(True)
        self.playlist_displayed_frame.set_child(self.playlist_displayed_box)

        self.playlist_info_frame = Gtk.Frame()
        self.playlist_info_frame.set_hexpand(True)
        self.playlist_info_frame.set_margin_bottom(10)
        self.playlist_displayed_box.append(self.playlist_info_frame)
        self.playlist_info_frame.hide()

        self.playlist_info_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.playlist_info_grid.set_hexpand(True)
        self.playlist_info_frame.set_child(self.playlist_info_grid)

        self.playlist_info_label = Gtk.Label()
        self.playlist_info_label.set_wrap(True)
        self.playlist_info_label.set_wrap_mode(Gtk.WrapMode.WORD)
        self.playlist_info_label.set_natural_wrap_mode(Gtk.NaturalWrapMode.WORD)
        self.playlist_info_label.set_halign(Gtk.Align.START)
        self.playlist_info_label.set_justify(Gtk.Justification.LEFT)
        self.playlist_info_label.set_max_width_chars(25)
        self.playlist_info_label.set_margin_start(10)
        self.playlist_info_label.set_margin_top(10)
        self.playlist_info_grid.attach(self.playlist_info_label, 0, 0, 6, 1)

        self.play_playlist_button = Gtk.Button()
        self.play_playlist_button.set_margin_start(10)
        self.play_playlist_button.set_margin_top(10)
        self.play_playlist_button.set_margin_bottom(10)
        self.play_playlist_button.set_child(
            Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-playback-start-symbolic")))
        self.playlist_info_grid.attach_next_to(self.play_playlist_button, self.playlist_info_label,
                                               Gtk.PositionType.BOTTOM, 1, 1)

        self.search_track_line = Gtk.SearchEntry(placeholder_text="Найти трек...", search_delay=100)
        self.search_track_line.set_hexpand(True)
        self.search_track_line.set_margin_start(10)
        self.search_track_line.set_margin_end(10)
        self.search_track_line.set_margin_top(10)
        self.search_track_line.set_margin_bottom(10)
        self.playlist_info_grid.attach_next_to(self.search_track_line, self.playlist_info_label,
                                               Gtk.PositionType.RIGHT, 1, 1)

        self.playlist_displayed_scrolled = Gtk.ScrolledWindow()
        self.playlist_displayed_scrolled.set_hexpand(True)
        self.playlist_displayed_scrolled.set_vexpand(True)
        self.playlist_displayed_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.playlist_displayed_box.append(self.playlist_displayed_scrolled)

        self.playlist_displayed_tracks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.playlist_displayed_tracks_box.set_valign(Gtk.Align.START)
        self.playlist_displayed_scrolled.set_child(self.playlist_displayed_tracks_box)

        self.playlists_widgets = []
        self.tracks_widgets = []

    def clear_playlists(self):
        [self.users_playlists_box.remove(self.users_playlists_box.get_first_child()) for _ in
         range(len(self.playlists_widgets))]
        self.playlists_widgets = []

    def clear_tracks(self):
        [self.playlist_displayed_tracks_box.remove(track) for track in self.tracks_widgets if
         track.get_parent() == self.playlist_displayed_tracks_box]
        self.tracks_widgets = []

    def add_playlist(self, playlist=None):
        playlist_widget = PlaylistWidget(playlist=playlist)
        self.playlists_widgets.append(playlist_widget)

    def add_track(self, track=None):
        track_widget = TrackWidget(track=track, track_number=len(self.tracks_widgets) + 1)
        self.tracks_widgets.append(track_widget)

    def redraw_playlists_widgets(self):
        [self.users_playlists_box.append(playlist) for playlist in self.playlists_widgets]

    def redraw_tracks_widgets(self):
        max_chars = len(str(len(self.tracks_widgets)))
        for widget in self.tracks_widgets:
            widget.track_number_label.set_size_request(10 * max_chars, -1)
            widget.playing_animation.set_size_request(10 * max_chars, 20)
            widget.playing_animation.drawing_area.set_size_request(10 * max_chars, 20)

        [self.playlist_displayed_tracks_box.append(track) for track in self.tracks_widgets]
