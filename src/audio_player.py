import pygame
pygame.init()
pygame.mixer.init()

import requests
import enum
import io

from misc import *


class AudioPlayer:
    def __init__(self):
        self.paused = False
        self._volume = 1.0
        self._duration = 0
        self._position_offset = 0
        self.content = None

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, volume):
        self._volume = volume

    @property
    def state(self):
        if self.paused:
            return AudioState.paused

        if pygame.mixer.music.get_busy():
            return AudioState.playing

        return AudioState.null

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration):
        self._duration = duration

    @property
    def position(self):
        if (pos := pygame.mixer.music.get_pos()) >= 0:
            return pos + self._position_offset
        return 0

    def load_from_file(self, filepath, filetype="mp3"):
        content = open(filepath, "rb")
        pygame.mixer.music.load(content, filetype)

        self._position_offset = 0
        self.content = content

        sound = pygame.mixer.Sound(content)
        self.duration = sound.get_length() * 1000

    def load_from_url(self, url):
        r = requests.get(url)
        content = io.BytesIO(r.content)
        pygame.mixer.music.load(content, namehint="mp3")

        self._position_offset = 0
        self.content = content

        sound = pygame.mixer.Sound(io.BytesIO(r.content))
        self.duration = round(sound.get_length() * 1000)

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)
        self.volume = volume

    def set_position(self, position):
        self._position_offset = position
        pygame.mixer.music.play(0, position / 1000)

    def play(self):
        if self.paused:
            self.paused = False
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.play()

    def pause(self):
        self.paused = True
        pygame.mixer.music.pause()

    @staticmethod
    def stop():
        pygame.mixer.music.stop()


class AudioState(enum.Enum):
    null = 0
    playing = 1
    paused = 2
