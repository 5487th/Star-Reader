import os, sys

# insures relative paths work even when
if getattr(sys, "frozen", False):
    os.chdir(sys._MEIPASS)

from PySide6.QtWidgets import QApplication, QWidget, QStackedWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView


from scripts.theme_manager import ThemeManager
from scripts.books_manager import BooksManager
from scripts.main_menu import MainMenu
from scripts.reader import Reader
from scripts.book_card import BookCard

app = QApplication(sys.argv)

# window configuration
window = QStackedWidget()
window.setObjectName("Window")
window.setAttribute(Qt.WA_StyledBackground, True)

window.setWindowTitle("Star Reader")
window.setWindowIcon(QIcon("assets/images/app-icon.png"))
window.resize(800, 600)

theme_manager = ThemeManager(app)
books_manager = BooksManager()

main_menu = MainMenu(theme_manager, books_manager, window)


def back_pressed(web_engine):
    # updating card display so that the card's referenced chapter number remains fresh and up to date
    main_menu.update_card_display()
    window.setCurrentWidget(main_menu)
    web_engine.deleteLater()


def book_opened(card: BookCard):
    reader = Reader(window, theme_manager, books_manager)
    reader.back_pressed.connect(back_pressed)
    window.addWidget(reader)

    reader.open_epub(
        card.book_directory, card.book_id, card.book_title, card.chapter_number
    )

    window.setCurrentWidget(reader)


main_menu.book_opened.connect(book_opened)

window.addWidget(main_menu)
window.setCurrentWidget(main_menu)

window.show()
sys.exit(app.exec())
