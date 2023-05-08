import math
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GLib


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
