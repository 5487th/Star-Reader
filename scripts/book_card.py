from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
    QLineEdit,
    QSizePolicy,
    QScrollArea,
    QMenu,
)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QIcon
from scripts.theme_manager import ThemedPushButton, ThemeManager
from scripts.books_manager import BooksManager
from scripts.flow_layout import FlowLayout
from PySide6.QtCore import Signal
from pathlib import Path


class BookCard(QWidget):
    delete_button_clicked: Signal = Signal(QWidget)
    cover_clicked: Signal = Signal(QWidget)

    def __init__(
        self,
        parent,
        book_id,
        book_directory,
        book_title,
        cover_path,
        chapter_number,
        theme_manager,
    ):
        super().__init__(parent)

        self.theme_manager = theme_manager
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.book_id = book_id
        self.book_title = book_title
        self.book_directory = book_directory
        self.chapter_number = chapter_number

        self.setMinimumSize(100, 200)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.vbox_layout = QVBoxLayout(self)
        self.setLayout(self.vbox_layout)

        if cover_path:
            self.cover = RoundedImage(
                self,
                cover_path,
                10,
                140,
                280,
            )
            self.cover.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.vbox_layout.addWidget(self.cover)

        else:
            self.cover = QLabel(book_title)
            self.cover.setObjectName("BookCoverTittle")
            self.cover.setFixedSize(140, 200)
            self.cover.setContentsMargins(10, 10, 10, 10)
            self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cover.setWordWrap(True)
            self.vbox_layout.addWidget(self.cover)
            self.cover.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.delete_button = ThemedPushButton(
            self.theme_manager,
            "assets/images/trash.svg",
            "assets/images/trash.svg",
            30,
            30,
            0,
            self,
        )
        self.delete_button.setStyleSheet(
            "background-color: rgba(32, 32, 33, 0.467);  border-radius: 10px; border-top-left-radius: 0px; border-bottom-right-radius: 0px;  "
        )
        self.delete_button.setFixedSize(40, 40)
        self.delete_button.raise_()
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.clicked.connect(
            lambda: self.delete_button_clicked.emit(self)
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Position button in the bottom-left corner
        margin = 5
        self.delete_button.move(
            9,
            self.height() - self.delete_button.height() - 9,
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.cover_clicked.emit(self)

        QWidget.mousePressEvent(self, event)


class RoundedImage(QLabel):
    def __init__(
        self, parent, image_path, border_radius=0, width=100, height=100, dpr=4
    ):
        super().__init__(parent)

        self.image_path = image_path
        self.border_radius = border_radius

        self.pixmap_image: QPixmap = QPixmap(self.image_path)
        self.setFixedSize(width, height)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def paintEvent(self, event):
        if self.pixmap_image.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.border_radius, self.border_radius)
        painter.setClipPath(path)

        # Scale image to fill the widget without distortion
        scaled = self.pixmap_image.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Center the image
        x = (scaled.width() - self.width()) // 2
        y = (scaled.height() - self.height()) // 2
        painter.drawPixmap(-x, -y, scaled)

        # resize the widget to fit the image
        self.setFixedSize(scaled.size())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
