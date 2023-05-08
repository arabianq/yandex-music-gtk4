import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GdkPixbuf


class PlaylistWidget(Gtk.Button):
    def __init__(self, playlist=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect("clicked", self.on_click)

        if playlist is None:
            cover = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 50, 50)
            cover.fill(0x00001230ff)
            cover = GdkPixbuf.Pixbuf.new_from_file("/src/data/yamusic-icon-svg.svg")
            playlist = {"title": "test", "kind": -1, "owner_id": -1, "cover": cover, "tracks": []}
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
        while not hasattr(library, "library_flag"):
            library = library.get_parent()
        library.emit("playlist_clicked", self)
