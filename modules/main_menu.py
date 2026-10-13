import sys
import os
from PySide6.QtWidgets import (
    QStackedWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon


class MainMenu(QWidget):

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent,
        )

        # main horizontal layout
        self.h_box = QHBoxLayout(self)
        self.h_box.setContentsMargins(0, 0, 0, 0)
        self.h_box.setSpacing(0)

        # the side bar
        self.side_bar = QWidget(self.parent())
        self.side_bar.setStyleSheet("background-color:#171B26;")
        self.side_bar.setMaximumWidth(50)
        self.h_box.addWidget(self.side_bar)

        # side var vbox
        self.side_bar_v_box = QVBoxLayout(self.side_bar)
        self.side_bar_v_box.setContentsMargins(0, 0, 0, 0)

        # star icon at the top of the side bar
        self.star_icon = QLabel("", self.side_bar)
        star_image = QPixmap("assets/star-no-background.svg").scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        star_image.setDevicePixelRatio(4)
        self.star_icon.setPixmap(star_image)
        self.side_bar_v_box.addWidget(self.star_icon, alignment=Qt.AlignTop)

        main_view = QStackedWidget(self.parent())

        self.h_box.addWidget(main_view)
