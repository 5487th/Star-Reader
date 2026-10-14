from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, Signal, QSize


class ThemeManager(QObject):
    set_to_dark: Signal = Signal()
    set_to_light: Signal = Signal()

    def __init__(self, app: QApplication, dark_mode: bool = True):
        super().__init__()

        self.app = app
        self.is_dark_mode = dark_mode

        with open("assets/themes/light.qss", "r", encoding="utf-8") as file:
            self.light_mode_qss = file.read()

        with open("assets/themes/dark.qss", "r", encoding="utf-8") as file:
            self.dark_mode_qss = file.read()

        if dark_mode:
            self.app.setStyleSheet(self.dark_mode_qss)
        else:
            self.app.setStyleSheet(self.light_mode_qss)

    def set_dark_mode(self):
        self.is_dark_mode = True
        self.app.setStyleSheet(self.dark_mode_qss)
        self.set_to_dark.emit()

    def set_light_mode(self):
        self.is_dark_mode = False
        self.app.setStyleSheet(self.light_mode_qss)
        self.set_to_light.emit()

    def toggle_theme(self):
        if self.is_dark_mode:
            self.set_light_mode()
        else:
            self.set_dark_mode()


class ThemedPushButton(QPushButton):
    def __init__(
        self,
        theme_manager: ThemeManager,
        icon_dark_path,
        icon_light_path,
        width,
        height,
        hover_increase_size,
        parent=None,
    ):
        super().__init__(parent)

        self.theme_manager = theme_manager
        self.theme_manager.set_to_dark.connect(self.set_to_dark)
        self.theme_manager.set_to_light.connect(self.set_to_light)

        self.icon_width = width
        self.icon_height = height

        self.on_hover_size_increase = hover_increase_size

        self.dark_image = QIcon(icon_dark_path)
        self.light_image = QIcon(icon_light_path)

        self.setIcon(self.light_image)
        if self.theme_manager.is_dark_mode:
            self.setIcon(self.dark_image)

        self.setIconSize(QSize(self.icon_width, self.icon_height))

    def set_to_dark(self):
        self.setIcon(self.dark_image)

    def set_to_light(self):
        self.setIcon(self.light_image)

    def enterEvent(self, event):
        self.setIconSize(
            QSize(
                self.icon_width + self.on_hover_size_increase,
                self.icon_height + self.on_hover_size_increase,
            )
        )
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIconSize((QSize(self.icon_width, self.icon_height)))
        super().leaveEvent(event)
