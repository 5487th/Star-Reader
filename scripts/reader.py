from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import QUrl, Signal, QEvent, QPropertyAnimation

import zipfile
from pathlib import Path
import xml.etree.ElementTree as Et
from urllib.parse import urljoin, urlsplit, unquote


from scripts.theme_manager import ThemeManager, ThemedPushButton
from scripts.books_manager import BooksManager


class Reader(QWebEngineView):
    back_pressed = Signal(QWebEngineView)

    def __init__(self, parent, theme_manager: ThemeManager, books_manager):

        super().__init__(parent)

        self.theme_manager: ThemeManager = theme_manager
        self.books_manager: BooksManager = books_manager

        self.unzip_folder: Path = Path("data") / "unzipped_temp"
        self.unzip_folder.mkdir(parents=True, exist_ok=True)

        self.opened_epub_path = None
        self.opened_epub_extracted_path = None

        self.opened_epub_id: int = None
        self.opened_epub_tittle: str = None

        self.opened_epub_chapter_number = 0

        self.opened_epub_chapter_paths_ordered = []

    def open_epub(self, path, id, tittle, chapter_number):
        self.opened_epub_path = Path(path)
        self.opened_epub_id = id
        self.opened_epub_tittle = tittle
        self.opened_epub_chapter_number = chapter_number

        self.load_epub_chapters(path)

        self.render_chapter(self.opened_epub_chapter_number)

        # top bar
        self.top_bar = QWidget(self)
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(0, 0, 20, 0)
        self.top_bar.setMaximumSize(600, 60)
        self.top_bar.setObjectName("TopBarBackground")
        self.top_bar.setLayout(self.top_bar_layout)

        self.back_button = ThemedPushButton(
            self.theme_manager,
            "assets/images/chevron-left.svg",
            "assets/images/chevron-left-dark.svg",
            30,
            30,
            1,
            self.top_bar,
        )
        self.back_button.clicked.connect(self.back_button_pressed)
        self.back_button.setFixedSize(40, 40)
        self.back_button.setObjectName("BackButton")
        self.top_bar_layout.addWidget(self.back_button)

        self.book_title = QLabel(self.opened_epub_tittle)
        self.book_title.setObjectName("BookTitle")
        self.top_bar_layout.addWidget(self.book_title)

        self.top_bar.move(10, 10)
        self.top_bar.adjustSize()
        self.top_bar.show()
        self.top_bar.raise_()

        # bottom bar
        self.bottom_bar = QWidget(self)
        self.bottom_bar_layout = QHBoxLayout(self.bottom_bar)
        self.bottom_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_bar.setMaximumSize(600, 60)
        self.bottom_bar.setObjectName("BottomBarBackground")
        self.bottom_bar.setLayout(self.bottom_bar_layout)

        self.previous_chapter_button = ThemedPushButton(
            self.theme_manager,
            "assets/images/chevron-left.svg",
            "assets/images/chevron-left-dark.svg",
            30,
            30,
            1,
            self.top_bar,
        )

        self.previous_chapter_button.setFixedSize(40, 40)
        self.previous_chapter_button.setObjectName("PreviousChapterButton")
        self.bottom_bar_layout.addWidget(self.previous_chapter_button)
        self.previous_chapter_button.clicked.connect(self.previous_chapter)

        self.chapter_number_dispaly = QLabel(
            f"{self.opened_epub_chapter_number}/{len(self.opened_epub_chapter_paths_ordered)-1}"
        )
        self.chapter_number_dispaly.setObjectName("ChapterNumberDisplay")
        self.bottom_bar_layout.addWidget(self.chapter_number_dispaly)

        self.next_chapter_button = ThemedPushButton(
            self.theme_manager,
            "assets/images/chevron-right.svg",
            "assets/images/chevron-right-dark.svg",
            30,
            30,
            1,
            self.top_bar,
        )
        self.next_chapter_button.clicked.connect(self.next_chapter)
        self.next_chapter_button.setFixedSize(40, 40)
        self.next_chapter_button.setObjectName("NextChapterButton")
        self.bottom_bar_layout.addWidget(self.next_chapter_button)

        x = self.parent().width() // 2 - (self.width() // 2)
        y = self.parent().height() - self.height() - 10

        self.bottom_bar.move(x, y)
        self.bottom_bar.adjustSize()
        self.bottom_bar.show()
        self.bottom_bar.raise_()

    def load_epub_chapters(self, path):
        # clears unzipped_temp folder
        for file in self.unzip_folder.rglob("*"):
            if file.is_file():
                file.unlink()

        self.opened_epub_chapter_paths_ordered.clear()

        if not self.opened_epub_path.is_file():
            return

        with zipfile.ZipFile(self.opened_epub_path) as z:
            z.extractall(self.unzip_folder / self.opened_epub_path.stem)
            self.opened_epub_extracted_path = (
                Path(self.unzip_folder) / self.opened_epub_path.stem
            )

        if not self.opened_epub_extracted_path.is_dir():
            return

        container = Et.parse(
            self.opened_epub_extracted_path / "META-INF" / "container.xml"
        ).getroot()

        ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}

        root_file = container.find("c:rootfiles/c:rootfile", ns)

        if root_file is None:
            return

        full_path = root_file.get("full-path")
        if not full_path:
            return
        opf_path = self.opened_epub_extracted_path / full_path

        opf = Et.parse(opf_path).getroot()

        ns = {
            "opf": "http://www.idpf.org/2007/opf",
            "dc": "http://purl.org/dc/elements/1.1/",
        }

        manifest = opf.find("opf:manifest", ns)
        spine = opf.find("opf:spine", ns)

        if manifest is None or spine is None:
            return

        manifest_items = {}
        for item in manifest.findall("opf:item", ns):
            manifest_items[item.get("id")] = item

        for itemref in spine.findall("opf:itemref", ns):
            item = manifest_items.get(itemref.get("idref"))
            if item is None:
                continue

            href = item.get("href")
            media_type = item.get("media-type")

            if item.get("media-type") != "application/xhtml+xml":
                continue

            properties = (item.get("properties") or "").split()

            if "nav" in properties:
                continue

            if itemref.get("linear") == "no":
                continue

            self.opened_epub_chapter_paths_ordered.append(
                self.resolve_epub_href(opf_path.parent, href)
            )

    def resolve_epub_href(self, opf_dir: Path, href: str) -> Path | None:
        if not href:
            return None
        return (opf_dir / unquote(href.split("#")[0])).resolve()

    def render_chapter(self, chapter_number):
        current_chapter = self.opened_epub_chapter_paths_ordered[chapter_number]

        self.load(QUrl.fromLocalFile(str(current_chapter)))

        self.apply_theme()

    def apply_theme(self):
        background = "#000000" if self.theme_manager.is_dark_mode else "#ffffff"
        text = "#ffffff" if self.theme_manager.is_dark_mode else "#000000"

        css = f"""
            html, body {{
                background-color: {background} !important;
                color: {text} !important;
            }}

            body, p, div, span, li, blockquote,
            h1, h2, h3, h4, h5, h6, td, th {{
                color: {text} !important;
                background-color: transparent !important;
            }}

            html {{
                background-color: {background} !important;
            }}
        """

        js = """
        (css) => {
            let style = document.getElementById('app-theme-style');
            if (!style) {
                style = document.createElement('style');
                style.id = 'app-theme-style';
                document.head.appendChild(style);
            }
            style.textContent = css;
        }
        """

        self.page().runJavaScript(js, lambda result: None)

    def back_button_pressed(self):
        self.books_manager.set_chapter_number(
            self.opened_epub_id, self.opened_epub_chapter_number
        )

        # clears unzipped_temp folder
        for file in self.unzip_folder.rglob("*"):
            if file.is_file():
                file.unlink()

        self.opened_epub_chapter_paths_ordered.clear()

        self.back_pressed.emit(self)

    def resizeEvent(self, event):
        x = self.parent().width() // 2 - (self.bottom_bar.width() // 2)
        y = self.parent().height() - self.bottom_bar.height() - 10
        self.bottom_bar.move(x, y)

        return super().resizeEvent(event)

    def previous_chapter(self):
        self.opened_epub_chapter_number = (
            self.opened_epub_chapter_number - 1
            if self.opened_epub_chapter_number > 0
            else self.opened_epub_chapter_number
        )
        self.chapter_number_dispaly.setText(
            f"{self.opened_epub_chapter_number}/{len(self.opened_epub_chapter_paths_ordered)-1}"
        )
        self.render_chapter(self.opened_epub_chapter_number)

        self.books_manager.set_chapter_number(
            self.opened_epub_id, self.opened_epub_chapter_number
        )

    def next_chapter(self):
        self.opened_epub_chapter_number = (
            self.opened_epub_chapter_number + 1
            if self.opened_epub_chapter_number
            < len(self.opened_epub_chapter_paths_ordered)
            else self.opened_epub_chapter_number
        )
        self.chapter_number_dispaly.setText(
            f"{self.opened_epub_chapter_number}/{len(self.opened_epub_chapter_paths_ordered)-1}"
        )
        self.render_chapter(self.opened_epub_chapter_number)
        self.books_manager.set_chapter_number(
            self.opened_epub_id, self.opened_epub_chapter_number
        )
