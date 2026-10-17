from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
    QLineEdit,
)
from PySide6.QtCore import Qt
from modules.theme_manager import ThemedPushButton, ThemeManager
from modules.books_manager import BooksManager


class Library(QWidget):
    def __init__(self, theme_manager, books_manager, parent):
        super().__init__(parent)
        self.theme_manager: ThemeManager = theme_manager
        self.books_manager: BooksManager = books_manager

        self.vbox_container = QVBoxLayout(self)
        self.setLayout(self.vbox_container)

        self.setContentsMargins(40, 30, 40, 30)

        self.heading = QLabel("Library", self)
        self.heading.setObjectName("LibraryHeader")
        self.vbox_container.addWidget(self.heading)

        # search bar
        self.search_bar_import_container = QWidget(self)
        self.search_import_container_hbox = QHBoxLayout(
            self.search_bar_import_container
        )
        self.search_import_container_hbox.setSpacing(80)
        self.search_import_container_hbox.setContentsMargins(0, 0, 0, 0)

        self.vbox_container.addWidget(self.search_bar_import_container)

        self.search_bar = QLineEdit(self.search_bar_import_container)
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("Search your library...")
        self.search_bar.setFixedHeight(40)
        self.search_import_container_hbox.addWidget(self.search_bar)

        self.search_icon = ThemedPushButton(
            theme_manager,
            "assets/icons/search.svg",
            "assets/icons/search-dark.svg",
            20,
            20,
            0,
            parent=self.search_bar,
        )

        self.search_icon.setFlat(True)
        self.search_icon.setFocusPolicy(Qt.NoFocus)
        self.search_icon.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.search_icon.setStyleSheet("background: transparent; border: none;")

        search_bar_layout = QHBoxLayout(self.search_bar)
        search_bar_layout.setContentsMargins(9, 0, 0, 0)
        search_bar_layout.addWidget(self.search_icon)
        search_bar_layout.addStretch()

        # books display

        self.vbox_container.addStretch()
