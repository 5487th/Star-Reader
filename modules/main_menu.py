from PySide6.QtWidgets import (
    QStackedWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
    QSizePolicy,
    QLineEdit,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from modules.theme_manager import ThemedPushButton, ThemeManager
from modules.books_manager import BooksManager


class MainMenu(QWidget):

    def __init__(
        self,
        theme_manager: ThemeManager,
        books_manager: BooksManager,
        parent=None,
    ):
        super().__init__(parent)

        self.theme_manager = theme_manager
        self.books_manager = books_manager

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

        # tabs container, which contains different tabs like library, favourites, etc..
        self.tabs_container = QWidget(self.side_bar)
        self.tabs_container.setObjectName("tabsContainer")

        tabs_vbox_layout = QVBoxLayout(self.tabs_container)
        tabs_vbox_layout.setSpacing(5)
        tabs_vbox_layout.setContentsMargins(2, 2, 2, 2)
        self.tabs_container.setLayout(tabs_vbox_layout)

        self.side_bar_v_box.addWidget(self.tabs_container, alignment=Qt.AlignHCenter)

        # library button
        self.library_button = ThemedPushButton(
            self.theme_manager,
            "assets/icons/library.svg",
            "assets/icons/library-dark.svg",
            25,
            25,
            0,
            self.tabs_container,
        )
        self.library_button.setFixedSize(QSize(35, 35))
        self.library_button.setObjectName("LibraryButton")
        self.library_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.library_button.clicked.connect(self.on_library_button_pressed)

        tabs_vbox_layout.addWidget(self.library_button, alignment=Qt.AlignHCenter)

        # favourites button
        self.favourites_button = ThemedPushButton(
            self.theme_manager,
            "assets/icons/heart.svg",
            "assets/icons/heart-dark.svg",
            25,
            25,
            0,
            self.tabs_container,
        )
        self.favourites_button.setFixedSize(QSize(35, 35))
        self.favourites_button.setObjectName("FavouritesButton-disable")
        self.favourites_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favourites_button.clicked.connect(self.on_favourites_button_pressed)

        tabs_vbox_layout.addWidget(self.favourites_button, alignment=Qt.AlignHCenter)

        # import button
        self.import_button = ThemedPushButton(
            theme_manager,
            "assets/icons/plus.svg",
            "assets/icons/plus-dark.svg",
            27,
            27,
            0,
            self.side_bar,
        )
        self.import_button.setObjectName("ImportButton")
        self.import_button.setFixedHeight(37)
        self.import_button.setFixedWidth(37)
        self.import_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.side_bar_v_box.addWidget(self.import_button, alignment=Qt.AlignHCenter)

        self.import_button.clicked.connect(self.on_import_button_pressed)

        self.side_bar_v_box.addStretch()

        # theme toggle button
        self.theme_toggle_button = ThemedPushButton(
            self.theme_manager,
            "assets/icons/moon.svg",
            "assets/icons/sun.svg",
            20,
            20,
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

        self.main_view = QStackedWidget(self)

        self.library = Library(self.theme_manager, self.books_manager, self.main_view)
        self.favourites = Favourites(
            self.theme_manager, self.books_manager, self.main_view
        )

        self.main_view.addWidget(self.library)
        self.main_view.addWidget(self.favourites)

        self.h_box.addWidget(self.main_view)

    def on_library_button_pressed(self, event):
        self.favourites_button.setObjectName("FavouritesButton-disable")
        self.library_button.setObjectName("LibraryButton")
        self.theme_manager.update()

        self.main_view.setCurrentWidget(self.library)
        pass

    def on_favourites_button_pressed(self, event):
        self.library_button.setObjectName("LibraryButton-disable")
        self.favourites_button.setObjectName("FavouritesButton")
        self.theme_manager.update()

        self.main_view.setCurrentWidget(self.favourites)
        pass

    def on_import_button_pressed(self, event):
        print("add pressed!")
        pass


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


class Favourites(QWidget):
    def __init__(self, theme_manager, books_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.books_manager = books_manager

        self.vbox_container = QVBoxLayout(self)
        self.setLayout(self.vbox_container)

        self.setContentsMargins(40, 30, 40, 30)

        self.heading = QLabel("Favourite", self)
        self.heading.setObjectName("FavouriteHeader")
        self.vbox_container.addWidget(self.heading)

        # search bar

        self.search_bar = QLineEdit(self)
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("Search your library...")
        self.search_bar.setFixedHeight(40)
        self.vbox_container.addWidget(self.search_bar)

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
