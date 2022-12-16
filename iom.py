from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QAudioOutput
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QListWidget
from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QSlider
from PyQt6.QtWidgets import QStyle
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget


class Playlist:
    """
    Class that represents a playlist.
    """

    def __init__(self) -> None:
        """
        Initialize the playlist by setting the songs list to an empty list and
        the current song index to -1.
        """

        self.songs: list[Path] = []
        self.__current_song_index: int = -1

    @property
    def songs(self) -> list[Path]:
        """
        Get the songs list.

        Returns:
            list[Path]: The songs list
        """

        return self.__songs

    @songs.setter
    def songs(self, songs: Iterable[str]) -> None:
        """
        Set the songs list.

        Args:
            songs (Iterable[str]): The songs list
        """

        self.__songs = list(map(Path, songs))
        self.__current_song_index = 0

    @property
    def next_song(self) -> str | None:
        """
        Get the next song in the playlist without changing the current song
        index.

        Returns:
            str | None: The next song in the playlist
        """

        if self.__current_song_index < len(self.songs) - 1:
            path = self.songs[self.__current_song_index + 1]
            return str(path)
        return None

    @property
    def previous_song(self) -> str | None:
        """
        Get the previous song in the playlist without changing the current song
        index.

        Returns:
            str | None: The previous song in the playlist
        """

        if self.__current_song_index > 0:
            path = self.songs[self.__current_song_index - 1]
            return str(path)
        return None

    def get_next_song(self) -> str | None:
        """
        Get the next song in the playlist and change the current song index.

        Returns:
            str | None: The next song in the playlist
        """

        if self.__current_song_index < len(self.songs) - 1:
            self.__current_song_index += 1
            path = self.songs[self.__current_song_index]
            return str(path)
        return None

    def get_previous_song(self) -> str | None:
        """
        Get the previous song in the playlist and change the current song index.

        Returns:
            str | None: The previous song in the playlist
        """

        if self.__current_song_index > 0:
            self.__current_song_index -= 1
            path = self.songs[self.__current_song_index]
            return str(path)
        return None


class AboutProjectWindow(QMessageBox):
    """
    Class that represents the about project window.
    """

    def __init__(self) -> None:
        """
        Initialize the about project window by setting the title and the text.
        """

        super().__init__()
        self.setWindowTitle('About Project')
        self.setText('This is a simple audio player written in Python using PyQt6.')
        self.setInformativeText('This project was created by:\nCristian Cristea & Cosmin Preotesei\nGroup 442A')
        self.setStandardButtons(QMessageBox.StandardButton.Ok)


class MusicPlayer(QMainWindow):
    """
    Class that represents the music player.
    """

    def __init__(self) -> None:
        """
        Initialize the music player by setting the window title, size and
        elements.
        """

        super().__init__()

        # Initialize the about project window
        self.about_project_window: AboutProjectWindow = AboutProjectWindow()

        # Initialize the playlist
        self.playlist: Playlist = Playlist()

        # Set the window title
        self.setWindowTitle('Audio player')

        # Set the window size
        self.setFixedSize(600, 600)

        # Initialize the two fonts
        self.font = QFont('Arial', 14)
        self.bold_font = QFont('Arial', 15, QFont.Weight.Bold)

        # Initialize the central widget for the window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Add the file menu to the menu bar
        file_menu = self.menuBar().addMenu('File')

        # Initialize and add the open action to the file menu
        open_action = QAction(text='&Open', parent=self, shortcut='Ctrl+O', triggered=self.open)
        file_menu.addAction(open_action)

        # Initialize and add the close action to the file menu
        close_action = QAction(text='&Close', parent=self, shortcut='Ctrl+Q', triggered=self.close)
        file_menu.addAction(close_action)

        # Add the about menu to the menu bar
        about_menu = self.menuBar().addMenu('About')

        # Initialize and add the about project action to the about menu
        about_project_action = QAction('About &Project', self, triggered=self.about_project)
        about_menu.addAction(about_project_action)

        # Initialize and add the about Qt action to the about menu
        about_qt_action = QAction(text='About &Qt', parent=self, triggered=QApplication.instance().aboutQt)
        about_menu.addAction(about_qt_action)

        # Initialize the main layout
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # Initialize the laout for the song progress bar
        audio_position = QHBoxLayout()
        self.layout.addLayout(audio_position)

        # Initialize and add the song progress label
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setFixedHeight(40)
        self.slider.sliderMoved.connect(self.set_position)
        audio_position.addWidget(self.slider)

        # Initialize the layout for the song play and pause controls
        audio_control = QHBoxLayout()
        self.layout.addLayout(audio_control)

        # Initialize and add the play button
        play_icon = QIcon.fromTheme('media-playback-start', self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        play_button = QPushButton(text=' Play', icon=play_icon, clicked=self.play)
        play_button.setFont(self.font)
        play_button.setFixedHeight(40)
        audio_control.addWidget(play_button)

        # Initialize and add the pause button
        pause_icon = QIcon.fromTheme('media-playback-pause', self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        pause_button = QPushButton(text=' Pause', icon=pause_icon, clicked=self.pause)
        pause_button.setFont(self.font)
        pause_button.setFixedHeight(40)
        audio_control.addWidget(pause_button)

        # Initialize the layout for the song previous and next controls
        song_control = QHBoxLayout()
        self.layout.addLayout(song_control)

        # Initialize and add the previous button
        previous_icon = QIcon.fromTheme('media-skip-backward', self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))
        previous_button = QPushButton(text=' Previous', icon=previous_icon, clicked=self.previous)
        previous_button.setFont(self.font)
        previous_button.setFixedHeight(40)
        song_control.addWidget(previous_button)

        # Initialize and add the next button
        next_icon = QIcon.fromTheme('media-skip-forward', self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward))
        next_button = QPushButton(text=' Next', icon=next_icon, clicked=self.next)
        next_button.setFont(self.font)
        next_button.setFixedHeight(40)
        song_control.addWidget(next_button)

        # Initialize the layout for the song volume controls
        volume_control = QHBoxLayout()
        self.layout.addLayout(volume_control)

        # Initialize the volume up button
        volume_up_icon = QIcon.fromTheme('audio-volume-high', self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        button_volume_up = QPushButton(text=' Volume up', icon=volume_up_icon, clicked=self.volume_up)
        button_volume_up.setFont(self.font)
        button_volume_up.setFixedHeight(40)

        # Initialize the volume down button
        volume_down_icon = QIcon.fromTheme('audio-volume-low', self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        button_volume_down = QPushButton(text=' Volume down', icon=volume_down_icon, clicked=self.volume_down)
        button_volume_down.setFont(self.font)
        button_volume_down.setFixedHeight(40)

        # Initialize and add the mute button
        mute_icon = QIcon.fromTheme('audio-volume-muted', self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        button_volume_mute = QPushButton(text=' Mute', icon=mute_icon, clicked=self.mute)
        button_volume_mute.setFont(self.font)
        button_volume_mute.setFixedHeight(40)

        # Add the volume buttons to the layout
        volume_control.addWidget(button_volume_down)
        volume_control.addWidget(button_volume_mute)
        volume_control.addWidget(button_volume_up)

        # Initialize and add the song list
        self.song_list = QListWidget()
        self.song_list.setFont(self.font)
        self.layout.addWidget(self.song_list)

        # Initialize the audio output destination
        self.audio_output = QAudioOutput()

        # Initialize the media player and set its audio output
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)

        # Connect the player signals to the appropriate actions
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)

    @staticmethod
    def remove_extension(file_name: str) -> str:
        """
        Remove the extension from a file name.

        Args:
            file_name (str): The file name

        Returns:
            str: The file name without the extension
        """

        return file_name[:file_name.rfind('.')]

    def set_position(self, position: int) -> None:
        """
        Set the position of the song to the given position.

        Args:
            position (int): The position
        """

        self.player.setPosition(position)

    def position_changed(self, position: int) -> None:
        """
        Set the slider position to the given position.

        Args:
            position (int): The position
        """

        self.slider.setValue(position)

    def duration_changed(self, duration: int) -> None:
        """
        Set the slider range to the given duration.

        Args:
            duration (int): The duration
        """

        self.slider.setRange(0, duration)

    def set_song_and_play(self, song: str) -> None:
        """
        Set the song to the given song, highlight it in the list and play it.

        Args:
            song (str): The song
        """

        # Get the song title from the song path and select it in the list
        song_title = song.split(os.sep)[-1]
        song_title = self.remove_extension(song_title)
        song_in_list = self.song_list.findItems(song_title, Qt.MatchFlag.MatchExactly)

        # Highlight the song in the list
        self.song_list.currentItem().setFont(self.font)
        self.song_list.setCurrentItem(song_in_list[0])
        self.song_list.currentItem().setFont(self.bold_font)

        # Set the song and play it
        self.player.setSource(QUrl.fromLocalFile(song))
        self.player.play()

    def play(self) -> None:
        """
        Play the current song.
        """

        self.player.play()

    def pause(self) -> None:
        """
        Pause the current song.
        """

        self.player.pause()

    def volume_up(self) -> None:
        """
        Increase the volume by 5% or to 100% if it is already at 95% or more.
        """

        current_volume = self.audio_output.volume()
        new_volume = current_volume + 0.05
        self.audio_output.setVolume(new_volume if new_volume <= 1 else 1)

    def volume_down(self) -> None:
        """
        Decrease the volume by 5% or to 0% if it is already at 5% or less.
        """

        current_volume = self.audio_output.volume()
        new_volume = current_volume - 0.05
        self.audio_output.setVolume(new_volume if new_volume >= 0 else 0)

    def mute(self) -> None:
        """
        Mute or unmute the audio output.
        """

        self.audio_output.setMuted(not self.audio_output.isMuted())

    def previous(self) -> None:
        """
        Go to the beginning of the song or to the previous song if the song is
        less than 5 seconds in.
        """

        if self.player.position() <= 5000 and self.playlist.previous_song is not None:
            self.set_song_and_play(self.playlist.get_previous_song())
        else:
            self.player.setPosition(0)
            self.player.play()

    def next(self) -> None:
        """
        Go to the next song.
        """

        if self.playlist.next_song is not None:
            self.set_song_and_play(self.playlist.get_next_song())

    def ensure_stopped(self) -> None:
        """
        Ensure that the player is stopped.
        """

        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.stop()

    def open(self) -> None:
        """
        Open a file dialog and set the playlist to the selected files.
        """

        self.ensure_stopped()

        # Initialize the file dialog and set its options and filters
        # Just audio files are allowed
        name_filter = 'Audio files (*.mp3 *.wav *.ogg *.flac *.aac)'
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter(name_filter)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, False)
        file_dialog.setOption(QFileDialog.Option.DontResolveSymlinks, False)

        # If the user selected files, set the playlist to the selected files
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            self.playlist.songs = file_dialog.selectedFiles()
            self.song_list.clear()
            song_names = (song.name for song in self.playlist.songs)
            song_names = map(self.remove_extension, song_names)
            song_names = (QListWidgetItem(name, self.song_list) for name in song_names)
            for item in song_names:
                item.setFlags(~Qt.ItemFlag.ItemIsEnabled)
            self.song_list.addItems(song_names)

        # Highlight the first song in the list and set the player to play it
        self.player.setSource(QUrl.fromLocalFile(str(self.playlist.songs[0])))
        self.song_list.setCurrentItem(self.song_list.item(0))
        self.song_list.currentItem().setFont(self.bold_font)

    def about_project(self) -> None:
        """
        Show the about project window.
        """

        self.about_project_window.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Ensure that the player is stopped and close the about project window.

        Args:
            event (QCloseEvent): The close event
        """

        self.ensure_stopped()
        self.about_project_window.close()
        event.accept()


def main() -> None:
    """
    The main function.
    """

    application = QApplication(sys.argv)
    music_player = MusicPlayer()
    music_player.show()

    sys.exit(application.exec())


if __name__ == '__main__':
    main()
