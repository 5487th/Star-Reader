import ebooklib
from pathlib import Path
import shutil
from ebooklib import epub
from peewee import SqliteDatabase, Model, CharField, AutoField, BooleanField


class Book(Model):
    id = AutoField()
    title = CharField()
    book_directory = CharField()
    author = CharField()
    cover_path = CharField()
    favourite = BooleanField(default=False)


class BooksManager:
    def __init__(self, root_path):
        self.books_data_base_path = Path(root_path).resolve() / "data" / "books.db"
        self.books_data_base_path.parent.mkdir(parents=True, exist_ok=True)

        self.books_folder = Path(root_path).resolve() / "data" / "books"
        self.books_folder.mkdir(parents=True, exist_ok=True)

        self.book_covers_folder = Path(root_path).resolve() / "data" / "covers"
        self.book_covers_folder.mkdir(parents=True, exist_ok=True)

        self.books_database = SqliteDatabase(self.books_data_base_path)

        Book.bind(self.books_database)

        # create database if it doesnt exist
        self.books_database.create_tables([Book], safe=True)

        self.books = Book.select()

    def add_epub(self, path_to_epub):

        file = Path(path_to_epub).resolve()
        if not file.exists():
            print("unable to find the epub file at the location: ", path_to_epub)
            return

        book = epub.read_epub(file)

        titles = book.get_metadata("DC", "title")
        title = titles[0][0] if titles else "Unknown Title"

        book_directory = self.books_folder / file.name
        shutil.copy(file, book_directory)

        authors = book.get_metadata("DC", "creator")
        author = authors[0][0] if authors else "Unknown Author"

        cover_path = None
        for item in book.get_items():
            if (
                "cover" in item.get_name().lower()
                or item.get_type() == ebooklib.ITEM_COVER
            ):
                cover_name = item.get_name()
                cover_path = self.book_covers_folder / cover_name

                cover_path.write_bytes(item.get_content())
                break

        Book.create(
            title=title,
            book_directory=book_directory,
            author=author,
            cover_path=cover_path,
        )
