from PySide6.QtWidgets import QApplication, QPushButton, QLabel, QGraphicsOpacityEffect
from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, Signal, QSize, Qt, QPropertyAnimation, QEasingCurve
from pathlib import Path


class ThemeManager(QObject):
    set_to_dark: Signal = Signal()
    set_to_light: Signal = Signal()

    def __init__(self, app: QApplication):
        super().__init__()

        self.app = app

        self.settings_file_path = Path("data/is_dark_mode.txt")

        if not self.settings_file_path.exists():
            self.settings_file_path.touch()
            self.settings_file_path.write_text("0")

        self.is_dark_mode = self.settings_file_path.read_text() == "1"

        self.transition_speed_MS = 300

        self.light_mode_qss = Path("assets/light.qss").read_text()
        self.dark_mode_qss = Path("assets/dark.qss").read_text()

        if self.is_dark_mode:
            self.app.setStyleSheet(self.dark_mode_qss)
        else:
            self.app.setStyleSheet(self.light_mode_qss)

        self._overlay = None

    def set_dark_mode(self):
        self.is_dark_mode = True
        self.app.setStyleSheet(self.dark_mode_qss)
        self.settings_file_path.write_text("1")
        self.set_to_dark.emit()

    def set_light_mode(self):
        self.is_dark_mode = False
        self.app.setStyleSheet(self.light_mode_qss)
        self.settings_file_path.write_text("0")
        self.set_to_light.emit()

    def toggle_theme(self):
        # grabs the active window
        window = self.app.activeWindow()

        # if the window is minimized or we are in a transition, instantly switch
        if self.app.activeWindow() is None or self._overlay is not None:
            if self.is_dark_mode:
                self.set_light_mode()
            else:
                self.set_dark_mode()
            return

        # captures a screen shot of the window and overlays it on the window
        self._overlay = QLabel(window)
        self._overlay.setPixmap(window.grab())
        self._overlay.setGeometry(window.rect())
        self._overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._overlay.show()
        self._overlay.raise_()

        # switching theme while the window is hidden by the overlay
        if self.is_dark_mode:
            self.set_light_mode()
        else:
            self.set_dark_mode()

        effect = QGraphicsOpacityEffect(self._overlay)
        self._overlay.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self._overlay)
        anim.setDuration(self.transition_speed_MS)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.finished.connect(self._end_transition)
        anim.start()

    def _end_transition(self):
        self._overlay.deleteLater()
        self._overlay = None

    def update(self):
        if self.is_dark_mode:
            self.set_dark_mode()
        else:
            self.set_light_mode()


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
