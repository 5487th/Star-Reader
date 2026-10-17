from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
    QSizePolicy,
    QLineEdit,
    QScrollArea,
    QMessageBox,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog

from scripts.theme_manager import ThemedPushButton, ThemeManager
from scripts.books_manager import BooksManager
from scripts.flow_layout import FlowLayout
from scripts.book_card import BookCard


class MainMenu(QWidget):
    def __init__(
        self, theme_manager: ThemeManager, books_manager: BooksManager, parent=None
    ):
        super().__init__(parent)

        self.theme_manager = theme_manager
        self.books_manager = books_manager

        self.cards: list[BookCard] = []

        # main horizontal layout
        self.h_box = QHBoxLayout(self)
        self.h_box.setContentsMargins(0, 0, 0, 0)
        self.h_box.setSpacing(0)

        # side bar, i dont even know why there is a comment here
        self.create_side_bar()

        # main view
        self.main_view = QWidget(self)
        self.h_box.addWidget(self.main_view)

        self.Main_view_vbox_container = QVBoxLayout(self.main_view)
        self.main_view.setLayout(self.Main_view_vbox_container)

        self.main_view.setContentsMargins(40, 30, 40, 30)

        self.heading = QLabel("Library", self)
        self.heading.setObjectName("LibraryHeader")
        self.Main_view_vbox_container.addWidget(self.heading)

        # search bar and import button
        self.create_search_bar_and_import_button()

        # book display area
        self.create_card_display()
        self.update_card_display()

    def create_side_bar(self):
        self.side_bar = QWidget(self)
        self.side_bar.setObjectName("SideBar")
        self.side_bar.setFixedWidth(50)
        self.h_box.addWidget(self.side_bar)

        self.side_bar_v_box = QVBoxLayout(self.side_bar)
        self.side_bar_v_box.setContentsMargins(0, 7, 0, 10)

        self.star_icon = QLabel("", self.side_bar)
        self.star_icon.setObjectName("star-icon")
        star_image = QPixmap("assets/images/star-no-background").scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        star_image.setDevicePixelRatio(5)
        self.star_icon.setPixmap(star_image)
        self.side_bar_v_box.addWidget(
            self.star_icon, alignment=Qt.AlignTop | Qt.AlignHCenter
        )

        self.theme_toggle_button = ThemedPushButton(
            self.theme_manager,
            "assets/images/moon.svg",
            "assets/images/sun.svg",
            30,
            30,
            5,
            self.side_bar,
        )
        self.theme_toggle_button.setObjectName("ThemeToggleButton")
        self.theme_toggle_button.clicked.connect(self.theme_manager.toggle_theme)
        self.theme_toggle_button.setFixedSize(QSize(40, 40))
        self.side_bar_v_box.addWidget(
            self.theme_toggle_button, alignment=Qt.AlignBottom | Qt.AlignHCenter
        )

    def create_search_bar_and_import_button(self):
        self.search_bar_import_container = QWidget(self)
        self.search_import_container_hbox = QHBoxLayout(
            self.search_bar_import_container
        )
        self.search_import_container_hbox.setSpacing(80)
        self.search_import_container_hbox.setContentsMargins(0, 0, 0, 0)

        self.Main_view_vbox_container.addWidget(self.search_bar_import_container)

        self.search_bar = QLineEdit(self.search_bar_import_container)
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("Search your library...")
        self.search_bar.setFixedHeight(40)
        self.search_bar.textChanged.connect(self.on_user_search)
        self.search_import_container_hbox.addWidget(self.search_bar)

        self.search_icon = ThemedPushButton(
            self.theme_manager,
            "assets/images/search.svg",
            "assets/images/search-dark.svg",
            20,
            20,
            0,
            parent=self.search_bar,
        )

        self.search_icon.setFlat(True)
        self.search_icon.setFocusPolicy(Qt.NoFocus)
        self.search_icon.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.search_icon.setObjectName("SearchIcon")

        search_bar_layout = QHBoxLayout(self.search_bar)
        search_bar_layout.setContentsMargins(9, 0, 0, 0)
        search_bar_layout.addWidget(self.search_icon)
        search_bar_layout.addStretch()

        self.import_button = ThemedPushButton(
            self.theme_manager,
            "assets/images/plus.svg",
            "assets/images/plus-dark.svg",
            30,
            30,
            0,
            self.side_bar,
        )
        self.import_button.setObjectName("ImportButton")
        self.import_button.setFixedSize(40, 40)
        self.import_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.import_button.clicked.connect(self.on_import_button_pressed)

        self.search_import_container_hbox.addWidget(
            self.import_button, alignment=Qt.AlignHCenter
        )

    def create_card_display(self):
        self.scrollable_area = QScrollArea(self)
        self.scrollable_area.setWidgetResizable(True)
        self.scrollable_area.setObjectName("BookCardsScrollArea")

        self.scrollable_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollable_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.Main_view_vbox_container.addWidget(self.scrollable_area)

        self.card_grid = QWidget()
        self.card_grid.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.card_grid.setObjectName("CardGrid")
        self.books_display_layout = FlowLayout(self.card_grid, margin=0)

        self.scrollable_area.setWidget(self.card_grid)

    def update_card_display(self):
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()

        for book in self.books_manager.get_all_books():
            card: BookCard = BookCard(
                self.card_grid,
                book.id,
                book.book_directory,
                book.title,
                book.cover_path,
                book.favourite,
                self.theme_manager,
            )
            card.delete_button_clicked.connect(self.on_delete_button_pressed)
            self.books_display_layout.addWidget(card)
            self.cards.append(card)

    def on_import_button_pressed(self, event):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "select your epub file/files", "", "E-books (*.epub)"
        )

        if file_paths:
            for path in file_paths:
                self.books_manager.add_epub(path)
        self.update_card_display()

    def on_delete_button_pressed(self, book_card: BookCard):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText(f"do you want to delete this book?")

        # 2. Add Standard Yes and No buttons
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        # 3. Set the default highlighted button
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        # 4. Show the dialog and capture the user's choice
        choice = msg_box.exec()

        if choice == QMessageBox.StandardButton.Yes:
            self.books_manager.remove_epub(book_card.book_id)
            self.update_card_display()

    def on_user_search(self, text):
        if text:
            for card in self.cards:
                if text.lower() in card.book_title.lower():
                    card.setVisible(True)
                else:
                    card.setVisible(False)
        else:
            for card in self.cards:
                card.setVisible(True)
