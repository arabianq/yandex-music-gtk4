from src.ui.track_playing_circle import TrackPlayingCircle

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk


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
            self.duration_ms = 120_000
        else:
            self.title = track.title.replace("&", "&amp;")
            self.artists = ", ".join([artist.name for artist in track.artists]).replace("&", "and")
            self.track_id = track.id
            self.track_available = track.available
            self.duration_ms = track.duration_ms

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
        while not hasattr(library, "library_flag"):
            library = library.get_parent()
        library.emit("track_clicked", self)
