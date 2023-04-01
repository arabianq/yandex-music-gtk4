import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gst


class AudioPlayer:
    def __init__(self):
        Gst.init(None)

        self.pipeline = Gst.Pipeline.new("audio-player")

        self.source = Gst.ElementFactory.make("filesrc", None)
        self.decoder = Gst.ElementFactory.make("decodebin", None)
        self.volume_controller = Gst.ElementFactory.make("volume", None)
        self.sink = Gst.ElementFactory.make("autoaudiosink", None)

        self.pipeline.add(self.source)
        self.pipeline.add(self.decoder)
        self.pipeline.add(self.volume_controller)
        self.pipeline.add(self.sink)

        self.source.link(self.decoder)
        self.volume_controller.link(self.sink)

        self.decoder.connect("pad-added", lambda d, pad: pad.link(self.volume_controller.get_static_pad(
            "sink")))

    @property
    def volume(self):
        return self.volume_controller.get_property("volume")

    @property
    def state(self):
        return self.pipeline.get_state(0).state

    @property
    def duration(self):
        duration = self.pipeline.query_duration(Gst.Format.TIME)
        if duration[0]:
            return duration[1]
        return 0

    @property
    def position(self):
        position = self.pipeline.query_position(Gst.Format.TIME)
        if position[0]:
            return position[1]
        return 0

    def load_from_file(self, filepath):
        self.stop()
        self.pipeline.remove(self.source)
        self.source = Gst.ElementFactory.make("filesrc", None)
        self.source.set_property("location", filepath)
        self.pipeline.add(self.source)
        self.source.link(self.decoder)

    def load_from_url(self, url):
        self.stop()
        self.pipeline.remove(self.source)
        self.source = Gst.ElementFactory.make("souphttpsrc", None)
        self.source.set_property("location", url)
        self.source.set_property("user-agent", "audio/mpeg")
        self.pipeline.add(self.source)
        self.source.link(self.decoder)

    def set_volume(self, volume):
        self.volume_controller.set_property("volume", volume)

    def set_position(self, position):
        self.pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, position)

    def play(self):
        self.pipeline.set_state(Gst.State.PLAYING)

    def pause(self):
        self.pipeline.set_state(Gst.State.PAUSED)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
