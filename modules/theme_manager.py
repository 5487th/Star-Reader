from PySide6.QtWidgets import QApplication


class ThemeManager:
    def __init__(self, app: QApplication, dark_mode: bool = True):
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

    def set_light_mode(self):
        self.is_dark_mode = False
        self.app.setStyleSheet(self.light_mode_qss)

    def toggle_theme(self):
        if self.is_dark_mode:
            self.set_light_mode()
        else:
            self.set_dark_mode()
