# ⭐ Star Reader

A clean, lightweight desktop EPUB reader built with Python and PySide6. Import your books, pick up where you left off, and read in light or dark mode.


## Features

- **Library view** with cover art in a responsive grid
- **Multi-book import** from the file picker (`.epub`)
- **Duplicate detection**: re-importing the same file is skipped (SHA-256 hash check)
- **Automatic cover extraction** from EPUB metadata, guide, spine, and image fallbacks
- **Search** your library by title
- **Resume reading**: your chapter position is saved per book
- **Chapter navigation** with a progress indicator
- **Light and dark themes** with a smooth fade transition; the theme is also applied to the book content and remembered between launches
- **Local storage**: books, covers, and reading progress are kept in a local SQLite database

## Requirements

- Python 3.10 or newer
- Packages:
  - [PySide6](https://pypi.org/project/PySide6/) (including QtWebEngine)
  - [EbookLib](https://pypi.org/project/EbookLib/)
  - [peewee](https://pypi.org/project/peewee/)

## Installation

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install PySide6 ebooklib peewee
```

## Usage

```bash
python main.py
```

1. Click the **+** button to import one or more `.epub` files.
2. Click a book cover to start reading.
3. Use the chevrons at the bottom to move between chapters.
4. Click the back arrow to return to the library. Your place is saved.
5. Use the moon/sun button in the sidebar to switch themes.
6. Hover over a cover and click the trash icon to delete a book.

## Project Structure

```
.
├── main.py                  # App entry point and window setup
├── scripts/
│   ├── main_menu.py         # Library screen (search, import, card grid)
│   ├── reader.py            # EPUB reader (QWebEngineView)
│   ├── book_card.py         # Book cover card widget
│   ├── books_manager.py     # Database + EPUB import/removal (peewee)
│   ├── cover_extractor.py   # Cover image detection from EPUB files
│   ├── theme_manager.py     # Light/dark theme handling
│   └── flow_layout.py       # Wrapping grid layout
├── assets/
│   ├── light.qss            # Light theme stylesheet
│   ├── dark.qss             # Dark theme stylesheet
│   └── images/              # Icons and app logo
└── data/                    # Created at runtime (see below)
```

## Where Your Data Lives

Star Reader creates a `data/` folder next to the app on first run:

| Path | Contents |
| --- | --- |
| `data/books.db` | SQLite database (titles, authors, reading progress) |
| `data/books/` | Copies of your imported EPUB files |
| `data/covers/` | Extracted cover images |
| `data/is_dark_mode.txt` | Saved theme preference |
| `data/unzipped_temp/` | Temporary extraction folder used while reading |

Your original EPUB files are copied, never modified.

## Building an Executable

The app detects when it is running from a PyInstaller bundle, so you can package it with something like:

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name "Star Reader" \
  --icon assets/images/app-icon.png \
  --add-data "assets;assets" \
  main.py
```

(Use `:` instead of `;` in `--add-data` on macOS/Linux.)

## Known Limitations

- EPUB only (no PDF, MOBI, etc.)
- No bookmarks, highlights, or font controls yet
- Progress is tracked per chapter, not per scroll position

## Roadmap

- [ ] Favourites
- [ ] Bookmarks
- [ ] Improved book cards showing author name and reading progress
- [ ] Edit book details (cover, title, author, and more)
- [ ] Scroll-position progress
- [ ] Support for other file types

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

Built with [PySide6](https://doc.qt.io/qtforpython-6/), [EbookLib](https://github.com/aerkalov/ebooklib), and [peewee](https://github.com/coleifer/peewee).
