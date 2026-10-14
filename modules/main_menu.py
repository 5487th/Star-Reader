import sys
import os
from PySide6.QtWidgets import (
    QStackedWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from modules.theme_manager import ThemedPushButton, ThemeManager


class MainMenu(QWidget):

    def __init__(
        self,
        theme_manager: ThemeManager,
        parent=None,
    ):
        super().__init__(parent)

        self.theme_manager = theme_manager

        # setting widget id(for qss) and enabling the background styling on this qwidget cause you need to do that for some reason
        self.setObjectName("MainMenu")
        self.setAttribute(Qt.WA_StyledBackground, True)

        # making sure it expands into the space provided
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # main horizontal layout
        self.h_box = QHBoxLayout(self)
        self.h_box.setContentsMargins(0, 0, 0, 0)
        self.h_box.setSpacing(0)

        # the side bar
        self.side_bar = QWidget(self)
        self.side_bar.setObjectName("SideBar")
        self.side_bar.setMaximumWidth(50)
        self.side_bar.setMinimumWidth(50)
        self.h_box.addWidget(self.side_bar)

        # side var vbox
        self.side_bar_v_box = QVBoxLayout(self.side_bar)
        self.side_bar_v_box.setContentsMargins(0, 7, 0, 10)

        # star icon at the top of the side bar
        self.star_icon = QLabel("", self.side_bar)
        self.star_icon.setObjectName("star-icon")
        star_image = QPixmap("assets/icons/star-no-background.svg").scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        star_image.setDevicePixelRatio(5)
        self.star_icon.setPixmap(star_image)
        self.side_bar_v_box.addWidget(
            self.star_icon, alignment=Qt.AlignTop | Qt.AlignHCenter
        )

        # separator under the star icon
        self.separator = QWidget(self.side_bar)
        self.separator.setObjectName("SideBarSeparator")
        self.separator.setFixedHeight(2)
        self.separator.setFixedWidth(40)
        self.separator.setAttribute(Qt.WA_StyledBackground, True)
        self.side_bar_v_box.addWidget(self.separator, alignment=Qt.AlignHCenter)

        self.side_bar_v_box.addStretch()

        self.theme_toggle_button = ThemedPushButton(
            self.theme_manager,
            "assets/icons/moon.svg",
            "assets/icons/sun.svg",
            30,
            30,
            5,
            self.side_bar,
        )
        self.theme_toggle_button.clicked.connect(self.theme_manager.toggle_theme)
        self.theme_toggle_button.setFixedSize(QSize(35, 35))

        self.theme_toggle_button.setStyleSheet(
            "background-color: transparent; border: none;"
        )

        self.side_bar_v_box.addWidget(
            self.theme_toggle_button, alignment=Qt.AlignTop | Qt.AlignHCenter
        )

        main_view = QStackedWidget(self)

        self.h_box.addWidget(main_view)
