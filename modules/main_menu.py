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

        main_view = QStackedWidget(self)

        self.h_box.addWidget(main_view)
