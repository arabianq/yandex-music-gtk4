import gi

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, WebKit

from multiprocessing import Pipe


class YandexOuathWindow(Gtk.Window):
    def __init__(self, pipe, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pipe = pipe

        self.set_title("Yandex Oauth")

        self.set_size_request(450, 700)
        self.set_resizable(False)

        self.webview = WebKit.WebView()
        self.set_child(self.webview)

        self.webview.connect("load-changed", self.uri_changed)
        self.connect("close_request", lambda *_args: self.quit())
        # self.connect("close_request", lambda *_args: self.get_application().on_quit_action())

        uri = "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d"
        self.webview.load_uri(uri)

    def uri_changed(self, *_args):
        uri = self.webview.get_uri()

        if "#access_token" not in uri:
            return

        token = uri.split("#access_token=")[1].split("&")[0]
        self.pipe.send(token)
        self.close()

    def quit(self):
        self.pipe.send(None)
        self.close()


class YandexOuathApp(Adw.Application):
    def __init__(self, pipe, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pipe = pipe

        self.window = None

        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.window = YandexOuathWindow(self.pipe, application=app)
        self.window.present()

    def on_quit_action(self):
        pass  # self.window.close()


def oauth():
    pipe1, pipe2 = Pipe()

    oauth_app = YandexOuathApp(pipe2, application_id="com.arabian.yamusic")
    oauth_app.run()

    token = pipe1.recv()
    return token


if __name__ == "__main__":
    print(oauth())
