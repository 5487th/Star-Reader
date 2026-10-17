from PySide6.QtWidgets import QApplication, QWidget, QStackedWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import sys

from scripts.theme_manager import ThemeManager
from scripts.books_manager import BooksManager
from scripts.main_menu import MainMenu

app = QApplication(sys.argv)

# window configuration
window = QStackedWidget()
window.setObjectName("Window")
window.setAttribute(Qt.WA_StyledBackground, True)

window.setWindowTitle("Star Reader")
window.setWindowIcon(QIcon("assets/app-icon.png"))
window.resize(800, 600)

theme_manager = ThemeManager(app)
books_manager = BooksManager()

main_menu = MainMenu(theme_manager, books_manager)

window.addWidget(main_menu)
window.setCurrentWidget(main_menu)

window.show()
sys.exit(app.exec())
