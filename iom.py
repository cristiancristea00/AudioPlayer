import sys
from pathlib import Path
from typing import Iterable

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QVBoxLayout, QWidget


class Playlist:

    def __init__(self) -> None:
        self.songs: list[Path] = []
        self.__current_song_index: int = None

    @property
    def songs(self) -> list[Path]:
        return self.__songs

    @songs.setter
    def songs(self, songs: Iterable[Path]) -> None:
        self.__songs = list(songs)
        self.__current_song_index = 0

    @property
    def current_song(self) -> Path:
        return self.songs[self.__current_song_index]


class MusicPlayer(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Audio player")

        self.setFixedSize(400, 150)

        self.font = QFont('Arial', 16)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        file_menu = self.menuBar().addMenu('File')

        open_action = QAction(text='Open', parent=self, shortcut='Ctrl+O')
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

        song_control = QHBoxLayout()
        self.layout.addLayout(song_control)

        play_button = QPushButton(text='Play', clicked=self.play)
        play_button.setFont(self.font)
        song_control.addWidget(play_button)

        pause_button = QPushButton(text='Pause', clicked=self.pause)
        pause_button.setFont(self.font)
        song_control.addWidget(pause_button)

        volume_control = QHBoxLayout()
        self.layout.addLayout(volume_control)

        button_volume_up = QPushButton(text='+', clicked=self.volume_up)
        button_volume_up.setFont(self.font)

        button_volume_down = QPushButton(text='-', clicked=self.volume_down)
        button_volume_down.setFont(self.font)

        button_volume_mute = QPushButton(text='Mute', clicked=self.mute)
        button_volume_mute.setFont(self.font)

        volume_control.addWidget(button_volume_up)
        volume_control.addWidget(button_volume_mute)
        volume_control.addWidget(button_volume_down)

        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        file_path = Path(__file__).parent / 'radiohead.mp3'
        source = QUrl.fromLocalFile(str(file_path))

        self.player.setSource(source)
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


def main() -> None:

    application = QApplication(sys.argv)
    music_player = MusicPlayer()
    music_player.show()

    sys.exit(application.exec())


if __name__ == '__main__':
    main()
