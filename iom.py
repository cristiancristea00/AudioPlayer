from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QListWidget, QMainWindow, QPushButton, QStyle, QVBoxLayout, QWidget


class Playlist:

    def __init__(self) -> None:
        self.songs: list[Path] = []
        self.__current_song_index: int = -1

    @property
    def songs(self) -> list[Path]:
        return self.__songs

    @songs.setter
    def songs(self, songs: Iterable[str]) -> None:
        self.__songs = list(map(Path, songs))
        self.__current_song_index = 0

    @property
    def next_song(self) -> str | None:
        if self.__current_song_index < len(self.songs) - 1:
            path = self.songs[self.__current_song_index + 1]
            return str(path)
        return None

    @property
    def previous_song(self) -> str | None:
        if self.__current_song_index > 0:
            path = self.songs[self.__current_song_index - 1]
            return str(path)
        return None

    def get_next_song(self) -> str | None:
        if self.__current_song_index < len(self.songs) - 1:
            self.__current_song_index += 1
            path = self.songs[self.__current_song_index]
            return str(path)
        return None

    def get_previous_song(self) -> str | None:
        if self.__current_song_index > 0:
            self.__current_song_index -= 1
            path = self.songs[self.__current_song_index]
            return str(path)
        return None


class MusicPlayer(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.playlist: Playlist = Playlist()

        self.setWindowTitle("Audio player")

        self.setFixedSize(500, 400)

        self.font = QFont('Arial', 14)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        file_menu = self.menuBar().addMenu('File')

        open_action = QAction(text='Open', parent=self, shortcut='Ctrl+O', triggered=self.open)
        file_menu.addAction(open_action)

        close_action = QAction(text='Close', parent=self, shortcut='Ctrl+Q', triggered=self.close)
        file_menu.addAction(close_action)

        about_menu = self.menuBar().addMenu('About')
        about_qt_action = QAction(text='About Qt', parent=self, triggered=QApplication.instance().aboutQt)
        about_menu.addAction(about_qt_action)

        about_project_action = QAction('About project', self)
        about_menu.addAction(about_project_action)

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        audio_control = QHBoxLayout()
        self.layout.addLayout(audio_control)

        play_icon = QIcon.fromTheme("media-playback-start", self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        play_button = QPushButton(text=' Play', icon=play_icon, clicked=self.play)
        play_button.setFont(self.font)
        audio_control.addWidget(play_button)

        pause_icon = QIcon.fromTheme("media-playback-pause", self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        pause_button = QPushButton(text=' Pause', icon=pause_icon, clicked=self.pause)
        pause_button.setFont(self.font)
        audio_control.addWidget(pause_button)

        song_control = QHBoxLayout()
        self.layout.addLayout(song_control)

        previous_icon = QIcon.fromTheme("media-skip-backward", self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))
        previous_button = QPushButton(text=' Previous', icon=previous_icon, clicked=self.previous)
        previous_button.setFont(self.font)
        song_control.addWidget(previous_button)

        next_icon = QIcon.fromTheme("media-skip-forward", self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward))
        next_button = QPushButton(text=' Next', icon=next_icon, clicked=self.next)
        next_button.setFont(self.font)
        song_control.addWidget(next_button)

        volume_control = QHBoxLayout()
        self.layout.addLayout(volume_control)

        volume_up_icon = QIcon.fromTheme("audio-volume-high", self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        button_volume_up = QPushButton(text=' Volume up', icon=volume_up_icon, clicked=self.volume_up)
        button_volume_up.setFont(self.font)

        volume_down_icon = QIcon.fromTheme("audio-volume-low", self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        button_volume_down = QPushButton(text=' Volume down', icon=volume_down_icon, clicked=self.volume_down)
        button_volume_down.setFont(self.font)

        mute_icon = QIcon.fromTheme("audio-volume-muted", self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        button_volume_mute = QPushButton(text=' Mute', icon=mute_icon, clicked=self.mute)
        button_volume_mute.setFont(self.font)

        volume_control.addWidget(button_volume_down)
        volume_control.addWidget(button_volume_mute)
        volume_control.addWidget(button_volume_up)

        self.song_list = QListWidget()
        self.layout.addWidget(self.song_list)

        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)

    def play(self) -> None:
        self.player.play()

    def pause(self) -> None:
        self.player.pause()

    def volume_up(self) -> None:
        current_volume = self.audio_output.volume()
        new_volume = current_volume + 0.05
        self.audio_output.setVolume(new_volume if new_volume <= 1 else 1)

    def volume_down(self) -> None:
        current_volume = self.audio_output.volume()
        new_volume = current_volume - 0.05
        self.audio_output.setVolume(new_volume if new_volume >= 0 else 0)

    def mute(self) -> None:
        self.audio_output.setMuted(not self.audio_output.isMuted())

    def previous(self) -> None:
        if self.player.position() <= 5000 and self.playlist.previous_song is not None:
            self.player.setSource(QUrl.fromLocalFile(self.playlist.get_previous_song()))
            self.player.play()
        else:
            self.player.setPosition(0)
            self.player.play()

    def next(self) -> None:
        if self.playlist.next_song is not None:
            self.player.setSource(QUrl.fromLocalFile(self.playlist.get_next_song()))
            self.player.play()

    def ensure_stopped(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.stop()

    @staticmethod
    def remove_extension(file_name: str) -> str:
        return file_name[:file_name.rfind('.')]

    def open(self) -> None:
        file_dialog = QFileDialog(self)

        name_filter = 'Audio files (*.mp3 *.wav *.ogg *.flac *.aac)'

        file_dialog.setNameFilter(name_filter)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, False)
        file_dialog.setOption(QFileDialog.Option.DontResolveSymlinks, False)

        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            self.playlist.songs = file_dialog.selectedFiles()

            self.song_list.clear()
            song_names = (song.name for song in self.playlist.songs)
            self.song_list.addItems(map(self.remove_extension, song_names))

        self.player.setSource(QUrl.fromLocalFile(str(self.playlist.songs[0])))


def main() -> None:

    application = QApplication(sys.argv)
    music_player = MusicPlayer()
    music_player.show()

    sys.exit(application.exec())


if __name__ == '__main__':
    main()
