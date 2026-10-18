import ebooklib
from pathlib import Path
from ebooklib import epub
from peewee import SqliteDatabase, Model, CharField, AutoField, IntegerField
import uuid
import hashlib
import shutil


from scripts.cover_extractor import extract_cover


class Book(Model):
    id = AutoField()
    title = CharField()
    book_directory = CharField()
    author = CharField()
    cover_path = CharField(null=True)
    chapter_number = IntegerField(default=0)


class BooksManager:
    def __init__(self):
        self.books_data_base_path = Path("data") / "books.db"
        self.books_data_base_path.parent.mkdir(parents=True, exist_ok=True)

        self.books_folder = Path("data") / "books"
        self.books_folder.mkdir(parents=True, exist_ok=True)

        self.book_covers_folder = Path("data") / "covers"
        self.book_covers_folder.mkdir(parents=True, exist_ok=True)

        self.books_database = SqliteDatabase(self.books_data_base_path)

        Book.bind(self.books_database)

        # create database if it doesnt exist
        self.books_database.create_tables([Book], safe=True)

    def add_epub(self, path_to_epub):
        # making sure book exists
        file = Path(path_to_epub).resolve()
        if not file.is_file():
            print("unable to find the epub file at the location: ", path_to_epub)
            return

        # makes sure user isnt trying to import an already existing book
        imported_book_hash = hashlib.sha256()

        with file.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                imported_book_hash.update(chunk)

        for path in self.books_folder.rglob("*.epub"):
            book_hash = hashlib.sha256()

            with Path(path).open("rb") as f:
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
        data = extract_cover(file)

        if data:
            ext = (
                ".png"
                if data.startswith(b"\x89PNG")
                else (
                    ".gif"
                    if data.startswith(b"GIF")
                    else (
                        ".webp"
                        if data[8:12] == b"WEBP"
                        else ".svg" if b"<svg" in data[:4096].lower() else ".jpg"
                    )
                )
            )
            cover_path = (
                self.book_covers_folder / f"{file.stem}_{uuid.uuid4().hex}{ext}"
            )
            cover_path.write_bytes(data)

        Book.create(
            title=title,
            book_directory=str(book_directory),
            author=author,
            cover_path=str(cover_path) if cover_path else None,
        )

    def remove_epub(self, id):
        book = Book.select().where(Book.id == id).first()

        if not book:
            print("unable to find book to delete.")
            return

        if book.cover_path:
            Path(book.cover_path).unlink(missing_ok=True)
        Path(book.book_directory).unlink(missing_ok=True)

        book.delete_instance()

    def get_all_books(self):
        return list(Book.select())

    def set_chapter_number(self, id, chapter_number):
        Book.update(chapter_number=chapter_number).where(Book.id == id).execute()
