import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GdkPixbuf


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
        self.player_controls_grid.attach_next_to(self.play_track_button, self.prev_track_button, Gtk.PositionType.RIGHT,
                                                 1, 3)

        # Adding next track button
        self.next_track_button = Gtk.Button()
        self.next_track_button.set_size_request(45, 45)
        self.next_track_button.set_vexpand(True)
        self.next_track_button.set_margin_bottom(10)
        self.next_track_button.set_valign(Gtk.Align.END)
        self.next_track_button.set_child(Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-skip-forward-symbolic")))
        self.player_controls_grid.attach_next_to(self.next_track_button, self.play_track_button, Gtk.PositionType.RIGHT,
                                                 1, 3)

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
        self.loop_playlist_button.set_child(Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("media-playlist-repeat")))
        self.player_controls_grid.attach(self.loop_playlist_button, 4, 1, 1, 1)

        # Adding track slider
        self.track_slider = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL, min=0, max=100, step=1)
        self.track_slider.set_hexpand(True)
        self.track_slider.set_valign(Gtk.Align.END)
        self.player_controls_grid.attach_next_to(self.track_slider, self.loop_playlist_button, Gtk.PositionType.RIGHT,
                                                 1, 1)

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
        self.player_controls_grid.attach_next_to(self.track_volume_button, self.track_timer, Gtk.PositionType.RIGHT, 1,
                                                 1)

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
        self.player_controls_grid.attach_next_to(self.show_queue_button, self.track_volume_button,
                                                 Gtk.PositionType.RIGHT, 1, 1)

        # Adding download track button
        self.download_track_button = Gtk.Button()
        self.download_track_button.set_size_request(30, 30)
        self.download_track_button.set_vexpand(True)
        self.download_track_button.set_margin_end(5)
        self.download_track_button.set_valign(Gtk.Align.END)
        self.download_track_button.set_child(Gtk.Image.new_from_gicon(Gio.ThemedIcon.new("folder-download-symbolic")))
        self.player_controls_grid.attach_next_to(self.download_track_button, self.show_queue_button,
                                                 Gtk.PositionType.RIGHT, 1, 1)
