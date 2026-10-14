import sys
import os

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
)
from PySide6.QtGui import QIcon
from modules.main_menu import MainMenu
from modules.theme_manager import ThemeManager

app = QApplication(sys.argv)

window = QMainWindow()

# window settings
window.setWindowTitle("Star Reader")
window.resize(800, 600)
window.setMinimumSize(800, 600)

# ensuring the task bar icon is the app icon
if os.name == "nt":
    import ctypes

    myappid = "mycompany.myproduct.subproduct.version"  # Arbitrary unique string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# this sets the icon and
window.setWindowIcon(QIcon("assets/app-icon.png"))


central_widget = QStackedWidget()
window.setCentralWidget(central_widget)

theme_manager = ThemeManager(app, False)

main_menu = MainMenu(theme_manager)
central_widget.addWidget(main_menu)

window.show()
sys.exit(app.exec())
