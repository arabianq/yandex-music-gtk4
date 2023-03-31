import math
import html

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GdkPixbuf, GObject, GLib, Gdk

import pathlib
WORK_DIR = str(pathlib.Path(__file__).parent.resolve())


class YamusicWindow(Gtk.Window):
    def __init__(self, start_window_size=(1200, 800), min_window_size=(800, 400), *args, **kwargs):
        super().__init__(*args, **kwargs)

        """ Parsing arguments """
        self.start_window_size = self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT = start_window_size
        self.min_window_size = self.MIN_WIDTH, self.MIN_HEIGHT = min_window_size

        """ Setting up window's params """
        self.set_default_size(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.set_title("Yamusic")

        # icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        # Gtk.IconTheme.add_search_path(icon_theme, f"{WORK_DIR}/data")
        # self.set_default_icon_name("yamusic-icon-png")
        # self.set_icon_name("yamusic-icon-png")

        """ Setting up header bar """
        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)

        # Creating boxes
        self.left_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.left_header_box.set_vexpand(True)
        self.left_header_box.set_hexpand(True)
        self.left_header_box.set_halign(Gtk.Align.START)
        self.left_header_box.set_margin_start(10)
        self.left_header_box.set_spacing(10)
        self.header.pack_start(self.left_header_box)

        self.center_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.center_header_box.set_vexpand(True)
        self.center_header_box.set_hexpand(True)
        self.center_header_box.set_halign(Gtk.Align.CENTER)
        self.center_header_box.set_spacing(10)
        self.header.set_title_widget(self.center_header_box)

        self.right_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.right_header_box.set_vexpand(True)
        self.right_header_box.set_hexpand(True)
        self.right_header_box.set_halign(Gtk.Align.END)
        self.right_header_box.set_spacing(10)
        self.header.pack_end(self.right_header_box)

        # Adding children to boxes
        self.header_spinner = Gtk.Spinner()
        self.left_header_box.append(self.header_spinner)

        self.header_library_button = Gtk.Button(label="Коллекция")
        self.center_header_box.append(self.header_library_button)

        self.header_main_page_button = Gtk.Button(label="Главная")
        self.center_header_box.append(self.header_main_page_button)

        # self.header.set_title_widget(self.header_box)

        """ Setting up main grid """
        self.main_grid = Gtk.Grid()
        self.set_child(self.main_grid)

        """ Setting up content box """
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.content_box.set_size_request(self.MIN_WIDTH, -1)
        self.content_box.set_hexpand(True)
        self.content_box.set_vexpand(True)

        # Adding children
        self.library = Library()
        self.library.set_size_request(self.MIN_WIDTH, self.MIN_HEIGHT * (5 / 6))
        self.content_box.append(self.library)

        self.main_grid.attach(self.content_box, 0, 0, 1, 1)

        """ Setting up media controls """
        self.player_controls_frame = PlayerControlsFrame()
        self.player_controls_frame.set_size_request(self.MIN_WIDTH, self.MIN_HEIGHT * (1 / 6))
        self.player_controls_frame.set_valign(Gtk.Align.END)

        self.main_grid.attach(self.player_controls_frame, 0, 1, 1, 1)


class Library(Gtk.Grid):
    __gsignals__ = {
        "playlist-clicked": (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)),
        "track-clicked": (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)),
    }

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
        self.users_playlists_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
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
        self.playlist_info_label.set_wrap(True)
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
        self.playlist_info_grid.attach_next_to(
            self.play_playlist_button, self.playlist_info_label, Gtk.PositionType.BOTTOM, 1, 1)

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
        [self.users_playlists_box.remove(self.users_playlists_box.get_first_child())
         for _ in range(len(self.playlists_widgets))]
        self.playlists_widgets = []

    def clear_tracks(self):
        [self.playlist_displayed_tracks_box.remove(track)
         for track in self.tracks_widgets if track.get_parent() == self.playlist_displayed_tracks_box]
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


class TrackWidget(Gtk.Button):
    def __init__(self, track=None, track_number=0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.track = track
        self.track_number = track_number

        if type(track) is dict:
            self.title = track["title"].replace("&", "&amp;")
            self.artists = ", ".join([artist for artist in track["artists"]]).replace("&", "and")
            self.track_id = track["id"]
            self.track_available = track["available"]
            self.duration_ns = 12 * 10e9
        else:
            self.title = track.title.replace("&", "&amp;")
            self.artists = ", ".join([artist.name for artist in track.artists]).replace("&", "and")
            self.track_id = track.id
            self.track_available = track.available
            self.duration_ns = None

        self.set_sensitive(self.track_available)

        self.connect("clicked", self.on_click)

        self.set_margin_bottom(3)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.grid = Gtk.Grid()
        self.set_child(self.grid)

        self.track_number_label = Gtk.Label(label=str(track_number))
        self.track_number_label.set_vexpand(True)
        self.track_number_label.set_halign(Gtk.Align.START)
        self.track_number_label.set_valign(Gtk.Align.CENTER)
        self.track_number_label.set_margin_end(10)
        self.grid.attach(self.track_number_label, 0, 0, 1, 1)

        self.label = Gtk.Label()
        self.label.set_wrap(True)
        self.label.set_wrap_mode(Gtk.WrapMode.WORD)
        self.label.set_natural_wrap_mode(Gtk.NaturalWrapMode.WORD)
        self.label.set_halign(Gtk.Align.START)
        self.label.set_hexpand(True)

        self.label.set_markup((f"<b>{self.title}</b>\n"
                              f"<small><i>{self.artists}</i></small>"))
        self.grid.attach_next_to(self.label, self.track_number_label, Gtk.PositionType.RIGHT, 1, 1)

        self.downloading_spinner_box = Gtk.Box()
        self.downloading_spinner = Gtk.Spinner()
        self.downloading_spinner_box.set_halign(Gtk.Align.END)
        self.downloading_spinner.set_halign(Gtk.Align.END)
        self.downloading_spinner_box.set_hexpand(True)
        self.downloading_spinner.set_hexpand(True)
        self.downloading_spinner_box.append(self.downloading_spinner)
        self.grid.attach_next_to(self.downloading_spinner_box, self.label, Gtk.PositionType.RIGHT, 1, 1)

        self.playing_animation = TrackPlayingCircle()
        self.playing_animation.set_halign(Gtk.Align.START)
        self.grid.attach_next_to(self.playing_animation, self.label, Gtk.PositionType.LEFT, 1, 1)

    def on_click(self, *_args):
        library = self.get_parent()
        while not isinstance(library, Library):
            library = library.get_parent()
        library.emit("track_clicked", self)


class TrackPlayingCircle(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_margin_end(10)

        self.drawing_area = Gtk.DrawingArea()
        self.set_size_request(20, 20)
        self.hide()

        self.drawing_area.set_draw_func(self.on_draw)
        self.drawing_area.set_size_request(20, 20)
        self.append(self.drawing_area)

        self.direction = 0
        self.min_radius = 4
        self.max_radius = 7
        self.radius = self.min_radius
        self.step = 0.1

        self.paused = False

    def on_draw(self, _widget, cr, *_args):
        cr.set_source_rgb(1, 1, 1)
        # cr.paint()
        width = self.drawing_area.get_allocated_width()
        height = self.drawing_area.get_allocated_height()

        # cr.rectangle(width / 2 - self.radius / 2, height / 2 - self.radius / 2, self.radius, self.radius)
        cr.arc(width / 2, height / 2, self.radius, 0, 2 * math.pi)
        cr.fill()
        pass

    def stop(self):
        self.get_parent().get_parent().track_number_label.show()
        self.hide()

    def pause(self):
        self.paused = True

    def play(self):
        self.get_parent().get_parent().track_number_label.hide()
        self.show()
        self.paused = False
        GLib.timeout_add(10, self.animate)

    def animate(self, *_args):
        if not self.is_visible() or self.paused:
            return False

        if self.direction == 0:
            if self.radius >= self.max_radius:
                self.direction = 1
            else:
                self.radius += self.step
                self.drawing_area.queue_draw()
        elif self.direction == 1:
            if self.radius <= self.min_radius:
                self.direction = 0
            else:
                self.radius -= self.step
                self.drawing_area.queue_draw()

        return True


class PlaylistWidget(Gtk.Button):
    def __init__(self, playlist=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect("clicked", self.on_click)

        if playlist is None:
            cover = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 50, 50)
            cover.fill(0x00001230ff)
            cover = GdkPixbuf.Pixbuf.new_from_file("/src/data/yamusic-icon-svg.svg")
            playlist = {
                "title": "test",
                "kind": -1,
                "owner_id": -1,
                "cover": cover,
                "tracks": []
            }
        self.playlist = playlist

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.box)

        self.cover_img = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(self.playlist["cover"]))

        self.cover_img.set_size_request(100, 100)
        self.cover_img.set_valign(Gtk.Align.CENTER)

        self.cover_img.set_margin_start(5)
        self.cover_img.set_margin_end(5)
        self.cover_img.set_margin_top(5)
        self.cover_img.set_margin_bottom(5)

        self.box.append(self.cover_img)
        self.title_label = Gtk.Label(label=self.playlist["title"])
        self.title_label.set_justify(Gtk.Justification.CENTER)
        self.title_label.set_vexpand(True)
        self.title_label.set_max_width_chars(10)
        self.title_label.set_wrap(True)
        self.title_label.set_wrap_mode(Gtk.WrapMode.WORD)
        self.box.append(self.title_label)

    def on_click(self, *_args):
        library = self.get_parent()
        while not isinstance(library, Library):
            library = library.get_parent()
        library.emit("playlist_clicked", self)


class PlayerControlsFrame(Gtk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_hexpand(True)
        self.set_vexpand(False)

        self.set_margin_start(5)
        self.set_margin_end(5)
        self.set_margin_top(5)
        self.set_margin_bottom(5)

        # Creating grid inside frame
        self.player_controls_grid = Gtk.Grid()
        self.set_child(self.player_controls_grid)
        self.player_controls_grid.set_column_spacing(5)
        self.player_controls_grid.set_row_spacing(5)

        # Adding prev track button
        self.prev_track_button = Gtk.Button()
        self.prev_track_button.set_size_request(45, 45)
        self.prev_track_button.set_vexpand(True)
        self.prev_track_button.set_margin_bottom(10)
        self.prev_track_button.set_margin_start(10)
        self.prev_track_button.set_valign(Gtk.Align.END)
        self.prev_track_button.set_child(Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-skip-backward-symbolic")))
        self.player_controls_grid.attach(self.prev_track_button, 0, 1, 1, 3)

        # Adding play button
        self.play_track_button = Gtk.Button()
        self.play_track_button.set_size_request(45, 45)
        self.play_track_button.set_vexpand(True)
        self.play_track_button.set_margin_bottom(10)
        self.play_track_button.set_valign(Gtk.Align.END)
        self.play_track_button.set_child(Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-playback-start-symbolic")))
        self.player_controls_grid.attach_next_to(
            self.play_track_button, self.prev_track_button, Gtk.PositionType.RIGHT, 1, 3)

        # Adding next track button
        self.next_track_button = Gtk.Button()
        self.next_track_button.set_size_request(45, 45)
        self.next_track_button.set_vexpand(True)
        self.next_track_button.set_margin_bottom(10)
        self.next_track_button.set_valign(Gtk.Align.END)
        self.next_track_button.set_child(Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-skip-forward-symbolic")))
        self.player_controls_grid.attach_next_to(
            self.next_track_button, self.play_track_button, Gtk.PositionType.RIGHT, 1, 3)

        # Adding shuffle button
        self.shuffle_playlist_button = Gtk.Button()
        self.shuffle_playlist_button.set_size_request(5, 5)
        self.shuffle_playlist_button.set_vexpand(True)
        self.shuffle_playlist_button.set_valign(Gtk.Align.END)
        self.shuffle_playlist_button.set_child(
            Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-playlist-shuffle-symbolic")))
        self.player_controls_grid.attach(self.shuffle_playlist_button, 3, 1, 1, 1)

        # Adding loop button
        self.loop_playlist_button = Gtk.Button()
        self.loop_playlist_button.set_size_request(10, 10)
        self.loop_playlist_button.set_vexpand(True)
        self.loop_playlist_button.set_valign(Gtk.Align.END)
        self.loop_playlist_button.set_child(
            Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-playlist-repeat")))
        self.player_controls_grid.attach(self.loop_playlist_button, 4, 1, 1, 1)

        # Adding track slider
        self.track_slider = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL, min=0, max=100, step=1)
        self.track_slider.set_hexpand(True)
        self.track_slider.set_valign(Gtk.Align.END)
        self.player_controls_grid.attach_next_to(
            self.track_slider, self.loop_playlist_button, Gtk.PositionType.RIGHT, 1, 1)

        self.track_slider_event_controller = Gtk.GestureClick()
        self.track_slider.add_controller(self.track_slider_event_controller)

        # Adding track cover
        image = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 50, 50)
        self.track_cover_img = Gtk.Image.new_from_pixbuf(image)
        self.track_cover_img.set_vexpand(True)
        self.track_cover_img.set_size_request(30, 30)
        self.track_cover_img.set_margin_top(10)
        self.track_cover_img.set_margin_start(10)

        self.player_controls_grid.attach(self.track_cover_img, 0, 0, 1, 1)

        # Adding track title
        self.track_title_label = Gtk.Label()
        self.track_title_label.set_selectable(True)
        self.track_title_label.set_vexpand(True)
        self.track_title_label.set_size_request(-1, -1)
        self.track_title_label.set_margin_top(10)
        self.track_title_label.set_halign(Gtk.Align.START)
        self.player_controls_grid.attach(self.track_title_label, 1, 0, 8, 1)

        # Adding track timer
        self.track_timer = Gtk.Label(label="\n00:00/00:00")
        self.track_timer.set_vexpand(True)
        self.track_timer.set_valign(Gtk.Align.CENTER)
        self.player_controls_grid.attach_next_to(self.track_timer, self.track_slider, Gtk.PositionType.RIGHT, 1, 1)

        # Adding volume_controller button
        self.track_volume_button = Gtk.Button()
        self.track_volume_button.set_size_request(30, 30)
        self.track_volume_button.set_vexpand(True)
        self.track_volume_button.set_margin_start(5)
        self.track_volume_button.set_valign(Gtk.Align.END)
        self.track_volume_button.set_child(Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("audio-volume-high-symbolic")))
        self.player_controls_grid.attach_next_to(
            self.track_volume_button, self.track_timer, Gtk.PositionType.RIGHT, 1, 1)

        self.track_volume_button_gesture = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        self.track_volume_button.add_controller(self.track_volume_button_gesture)
        # self.track_volume_button_gesture.connect("scroll", lambda _controller, _dx, dy: print(args))

        # Adding volume_controller popover
        self.volume_popover = Gtk.Popover()
        self.volume_popover.set_position(Gtk.PositionType.TOP)
        self.volume_popover.set_parent(self.track_volume_button)

        # Adding volume slider
        self.volume_slider = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.VERTICAL, min=0, max=100, step=0.5)
        self.volume_slider.set_value(100)
        self.volume_slider.set_inverted(True)
        self.volume_slider.set_size_request(1, 100)
        self.volume_popover.set_child(self.volume_slider)

        # Adding show playlist button
        self.show_queue_button = Gtk.Button()
        self.show_queue_button.set_size_request(30, 30)
        self.show_queue_button.set_vexpand(True)
        self.show_queue_button.set_valign(Gtk.Align.END)
        self.show_queue_button.set_child(Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("format-indent-less-symbolic")))
        self.player_controls_grid.attach_next_to(
            self.show_queue_button, self.track_volume_button, Gtk.PositionType.RIGHT, 1, 1)

        # Adding download track button
        self.download_track_button = Gtk.Button()
        self.download_track_button.set_size_request(30, 30)
        self.download_track_button.set_vexpand(True)
        self.download_track_button.set_margin_end(5)
        self.download_track_button.set_valign(Gtk.Align.END)
        self.download_track_button.set_child(Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("folder-download-symbolic")))
        self.player_controls_grid.attach_next_to(
            self.download_track_button, self.show_queue_button, Gtk.PositionType.RIGHT, 1, 1)