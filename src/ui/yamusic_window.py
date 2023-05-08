from src.ui.library import Library
from src.ui.player_controls import PlayerControlsFrame

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk



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
