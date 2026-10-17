import ebooklib
from pathlib import Path
import shutil
from ebooklib import epub
from peewee import SqliteDatabase, Model, CharField, AutoField, BooleanField
import uuid
import hashlib


class Book(Model):
    id = AutoField()
    title = CharField()
    book_directory = CharField()
    author = CharField()
    cover_path = CharField(null=True)
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

    def add_epub(self, path_to_epub):
        # making sure book exists
        file = Path(path_to_epub).resolve()
        if not file.exists():
            print("unable to find the epub file at the location: ", path_to_epub)
            return

        # makes sure user isnt trying to import an already existing book
        imported_book_hash = hashlib.sha256()

        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                imported_book_hash.update(chunk)

        for path in self.books_folder.rglob("*.epub"):
            book_hash = hashlib.sha256()

            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    book_hash.update(chunk)

            if imported_book_hash.digest() == book_hash.digest():
                print("book already imported!")
                return

        book = epub.read_epub(file)

        # getting tittle
        titles = book.get_metadata("DC", "title")
        title = titles[0][0] if titles else "Unknown Title"

        # giving each book unique name so that they dont overwrite each other
        book_directory = (
            self.books_folder / f"{file.stem}_{uuid.uuid4().hex}{file.suffix}"
        )
        shutil.copy(file, book_directory)

        # getting author
        authors = book.get_metadata("DC", "creator")
        author = authors[0][0] if authors else "Unknown Author"

        # getting cover
        cover_path = None
        for item in book.get_items():
            is_cover_type = item.get_type() == ebooklib.ITEM_COVER
            is_cover_image = (
                item.get_type() == ebooklib.ITEM_IMAGE
                and "cover" in item.get_name().lower()
            )

            if is_cover_type or is_cover_image:
                ext = Path(item.get_name()).suffix or ".jpg"
                cover_path = (
                    self.book_covers_folder / f"{file.stem}_{uuid.uuid4().hex}{ext}"
                )
                cover_path.write_bytes(item.get_content())
                break

        Book.create(
            title=title,
            book_directory=book_directory,
            author=author,
            cover_path=cover_path,
        )

    def set_to_favourite(self, path):
        return (
            Book.update(favourite=True)
            .where(Book.book_directory == str(path))
            .execute()
        )

    def un_set_to_favourite(self, path):
        return (
            Book.update(favourite=False)
            .where(Book.book_directory == str(path))
            .execute()
        )

    def get_all_books(self):
        return list(Book.select())

    def get_all_favourite_books(self):
        return list(Book.select().where(Book.favourite == True))
