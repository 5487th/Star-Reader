import posixpath, re, tempfile
from urllib.parse import unquote
import ebooklib
from ebooklib import epub

_MAGIC = (
    b"\xff\xd8\xff",
    b"\x89PNG\r\n\x1a\n",
    b"GIF87a",
    b"GIF89a",
    b"BM",
    b"II*\x00",
    b"MM\x00*",
)
_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp")


def extract_cover(f):
    ok = (
        lambda d: bool(d)
        and len(d) > 15
        and (
            d.startswith(_MAGIC)
            or (d[:4] == b"RIFF" and d[8:12] == b"WEBP")
            or b"<svg" in d[:4096].lower()
        )
    )
    isimg = lambda i: (getattr(i, "media_type", "") or "").lower().startswith(
        "image/"
    ) or (i.get_name() or "").lower().endswith(_EXT)

    def data(i):
        try:
            d = i.get_content()
        except Exception:
            return None
        return d if ok(d) else None

    def find(h, base=None):
        h = unquote((h or "").split("#")[0].split("?")[0]).strip()
        if not h:
            return None
        c = (
            [posixpath.normpath(posixpath.join(posixpath.dirname(base), h))]
            if base
            else []
        ) + [posixpath.normpath(h), h.lstrip("/")]
        for x in c:
            i = book.get_item_with_href(x)
            if i is not None:
                return i
        low, names, fb = (
            {x.lower() for x in c},
            {posixpath.basename(x).lower() for x in c},
            None,
        )
        for i in book.get_items():
            n = (i.get_name() or "").lower()
            if n in low:
                return i
            if fb is None and posixpath.basename(n) in names:
                fb = i
        return fb

    def page(p):
        try:
            t = p.get_content().decode("utf-8", "ignore")
        except Exception:
            return None
        srcs = [
            m[1]
            for m in re.findall(
                r"<\s*(?:img|image)\b[^>]*?(?:src|href)\s*=\s*([\"'])(.*?)\1",
                t,
                re.I | re.S,
            )
        ]
        srcs += re.findall(r"url\(\s*[\"']?([^)\"']+)[\"']?\s*\)", t, re.I)
        for s in srcs:
            if not s.startswith("data:"):
                d = data(find(s, p.get_name()))
                if d:
                    return d

    opts = {"ignore_ncx": True, "ignore_missing_css": True}
    try:
        if hasattr(f, "read"):
            with tempfile.NamedTemporaryFile(suffix=".epub") as t:
                t.write(f.read())
                t.flush()
                book = epub.read_epub(t.name, opts)
        else:
            book = epub.read_epub(str(f), opts)
    except Exception:
        return None

    items = list(book.get_items())
    imgs = [i for i in items if isimg(i)]
    doc = lambda i: i is not None and i.get_type() == ebooklib.ITEM_DOCUMENT

    def cands():
        for i in items:
            p = getattr(i, "properties", None) or []
            if "cover-image" in (p.split() if isinstance(p, str) else p):
                yield data(i)
        try:
            metas = book.get_metadata("OPF", "cover") or []
        except Exception:
            metas = []
        for _, a in metas:
            r = (a or {}).get("content") or (a or {}).get("name")
            if r:
                i = book.get_item_with_id(r)
                yield data(i)
                if i is not None and not isimg(i):
                    yield page(i)
                yield data(find(r))
        for i in book.get_items_of_type(ebooklib.ITEM_COVER):
            yield data(i)
        for g in getattr(book, "guide", None) or []:
            if (g.get("type") or "").lower() in ("cover", "title-page", "coverimage"):
                i = find(g.get("href"))
                if i is not None:
                    yield data(i) if isimg(i) else page(i)
        named = [
            i
            for i in items
            if doc(i) and "cover" in ((i.get_name() or "") + (i.get_id() or "")).lower()
        ]
        spine = [
            i
            for i in (
                book.get_item_with_id(e[0] if isinstance(e, (tuple, list)) else e)
                for e in book.spine or []
            )
            if doc(i)
        ]
        for p in named + spine[:1]:
            yield page(p)
        like = [
            i
            for i in imgs
            if "cover" in ((i.get_id() or "") + (i.get_name() or "")).lower()
        ]
        yield max(filter(None, map(data, like)), key=len, default=None)
        yield max(
            (d for d in map(data, imgs) if d and len(d) > 2048), key=len, default=None
        )

    return next(filter(None, cands()), None)
