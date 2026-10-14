#!/usr/bin/env python3
"""
build.py  -  turns the `projects/` and `pages/` folders into a static website.

    python3 build.py            build the site into _site/
    python3 build.py --serve    build, then preview at http://localhost:8000

ADDING A PROJECT
    1. make a folder inside projects/  -> the folder name is the project title
    2. drop images in it (jpg, png, gif, webp), optionally videos (mp4, webm) and pdfs
    3. add a text.md (or text.txt) with the description
    4. push. GitHub builds and publishes it automatically.

    Images are shown in filename order (01.jpg, 02.jpg, ...). A file called
    cover.jpg (or the first image) is used as the thumbnail on the front page.
    Folders starting with "_" are treated as drafts and are not published.

Only needs Python 3. Pillow (pip install pillow) is optional but recommended:
with it, images are resized, stripped of EXIF/GPS data and the glitched
black & white thumbnails are generated. GitHub's build always uses Pillow.
"""

import hashlib
import html
import os
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path

# --------------------------------------------------------------------------
# SETTINGS - change freely
# --------------------------------------------------------------------------
SITE = {
    "name": "Martin Guevara-Kunerth",
    "description": "Martin Guevara-Kunerth - Multimedia-Künstler und Fotograf, Graz.",
    "lang": "de",
    "url": "https://martinguevarakunerth.com",  # used for sitemap / share previews
    "base": "",                                # leave empty when using your own domain
}
MAX_IMAGE = 1800        # longest edge (px) of images on project pages
JPEG_QUALITY = 82
THUMB_WIDTH = 900       # colour thumbnail on the front page
GLITCH_AMOUNT = 1.0     # 0 = clean black & white thumbnails, 2 = very broken
# --------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
PROJECTS = ROOT / "projects"
PAGES = ROOT / "pages"
THEME = ROOT / "theme"
OUT = Path(os.environ.get("SITE_OUT", ROOT / "_site"))
CACHE = ROOT / ".cache"
CACHE_VERSION = "5"

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff"}
VIDEO_EXT = {".mp4", ".webm", ".m4v"}
FILE_EXT = {".pdf"}
TEXT_NAMES = ["text.md", "text.txt", "readme.md", "readme.txt", "info.md", "info.txt"]

try:
    from PIL import Image, ImageOps
    Image.MAX_IMAGE_PIXELS = 300_000_000
    HAVE_PIL = True
except ImportError:  # still works, just without resizing / glitch thumbnails
    HAVE_PIL = False


# ---------------------------------------------------------------- helpers
def nfc(s):
    return unicodedata.normalize("NFC", s)


def slugify(name):
    s = nfc(name).lower()
    for a, b in {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}.items():
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "project"


def natural_key(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def esc(s):
    return html.escape(str(s), quote=True)


def human_size(n):
    if n < 1024 * 1024:
        return f"{max(1, round(n / 1024))} kB"
    return f"{n / 1024 / 1024:.1f} MB"


def first_year(value):
    m = re.search(r"\d{4}", value or "")
    return int(m.group()) if m else 0


# ---------------------------------------------------------------- text
def split_front_matter(raw):
    """Optional header between --- lines:   year: 2020 / subtitle: ... / order: 1"""
    meta = {}
    raw = raw.replace("\r\n", "\n").lstrip("﻿")
    if raw.startswith("---\n"):
        end = raw.find("\n---", 4)
        if end != -1:
            for line in raw[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
            raw = raw[end + 4:].lstrip("-").lstrip("\n")
    return meta, raw


def inline(s):
    s = esc(s)
    stash = []

    def keep(h):
        stash.append(h)
        return f"\x00{len(stash) - 1}\x00"

    def link(url, text):
        url_attr = url.replace('"', "%22")
        ext = url.startswith("http")
        cls = ' class="ext" rel="noopener"' if ext else ""
        return keep(f'<a href="{url_attr}"{cls}>{text}</a>')

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: link(m.group(2), m.group(1)), s)
    s = re.sub(r"(?<![\w/=\"])(https?://[^\s<]+[^\s<.,;:!?)])",
               lambda m: link(m.group(1), re.sub(r"^https?://(www\.)?", "", m.group(1))), s)
    s = re.sub(r"(?<![\w@./])([\w.+-]+@[\w-]+(?:\.[\w-]+)+)",
               lambda m: keep(f'<a href="mailto:{m.group(1)}">{m.group(1)}</a>'), s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], s)


def markdown(text):
    """A tiny Markdown subset: # headings, paragraphs, line breaks, - lists,
    **bold**, *italic*, [links](https://...), bare urls/e-mails and --- lines."""
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l.rstrip() for l in block.strip("\n").split("\n")]
        if not lines or not lines[0].strip():
            continue
        if re.fullmatch(r"\s*(-{3,}|\*{3,})\s*", block):
            out.append("<hr>")
            continue
        m = re.match(r"(#{1,3})\s+(.*)", lines[0])
        if m:
            level = len(m.group(1)) + 1  # page title is the h1
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            lines = lines[1:]
            if not lines:
                continue
        if all(re.match(r"\s*[-*]\s+", l) for l in lines):
            items = "".join("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", l)) + "</li>" for l in lines)
            out.append(f"<ul>{items}</ul>")
            continue
        out.append("<p>" + "<br>\n".join(inline(l.strip()) for l in lines) + "</p>")
    return "\n".join(out)


def strip_markup(text, n=160):
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    t = re.sub(r"[#*`>_]", "", t)
    t = " ".join(t.split())
    return (t[: n - 1] + "…") if len(t) > n else t


# ---------------------------------------------------------------- images
_HASHES = {}


def file_hash(path):
    """content hash (not mtime: git checkouts reset modification times)"""
    if path not in _HASHES:
        h = hashlib.sha1()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        _HASHES[path] = h.hexdigest()
    return _HASHES[path]


def cache_path(src, tag, ext):
    key = f"{file_hash(src)}|{tag}|{CACHE_VERSION}|" \
          f"{MAX_IMAGE}|{JPEG_QUALITY}|{THUMB_WIDTH}|{GLITCH_AMOUNT}"
    h = hashlib.sha1(key.encode()).hexdigest()[:16]
    return CACHE / f"{h}{ext}"


def image_size(path):
    if not HAVE_PIL:
        return None
    try:
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def web_image(src, dst_dir, stem):
    """Resized, EXIF-free copy of an image. Animated GIFs are kept as they are."""
    ext = src.suffix.lower()
    if not HAVE_PIL:
        dst = dst_dir / f"{stem}{ext}"
        shutil.copy2(src, dst)
        return dst, None
    with Image.open(src) as im:
        animated = getattr(im, "is_animated", False)
        if ext == ".gif" or animated:
            dst = dst_dir / f"{stem}{ext}"
            shutil.copy2(src, dst)
            return dst, im.size
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        out_ext = ".png" if has_alpha else ".jpg"
        cached = cache_path(src, "web", out_ext)
        if not cached.exists():
            im = ImageOps.exif_transpose(im)
            im = im.convert("RGBA" if has_alpha else "RGB")
            im.thumbnail((MAX_IMAGE, MAX_IMAGE), Image.LANCZOS)
            CACHE.mkdir(exist_ok=True)
            if has_alpha:
                im.save(cached, optimize=True)
            else:
                im.save(cached, quality=JPEG_QUALITY, optimize=True, progressive=True)
        dst = dst_dir / f"{stem}{out_ext}"
        shutil.copy2(cached, dst)
        return dst, image_size(dst)


def representative_frame(im):
    """first frame of a still image; for animations the brightest of a few frames"""
    if not getattr(im, "is_animated", False):
        return ImageOps.exif_transpose(im).convert("RGB")
    best, best_val = None, -1
    n = im.n_frames
    for i in sorted({int(n * k / 8) for k in range(8)}):
        im.seek(i)
        fr = im.convert("RGB")
        from PIL import ImageStat
        val = ImageStat.Stat(fr.convert("L")).mean[0]
        if val > best_val:
            best, best_val = fr.copy(), val
    return best


def glitch(rgb, seed):
    """Black & white thumbnail with horizontal slice shifts, smeared rows and
    scan bands. Deterministic: the same image always gets the same glitch."""
    import random
    from PIL import ImageEnhance
    rnd = random.Random(seed)
    g = ImageOps.autocontrast(rgb.convert("L"), cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(1.25)
    w, h = g.size
    out = g.copy()
    amt = GLITCH_AMOUNT
    if amt <= 0:
        return out
    # 1. shifted slices
    for _ in range(int(rnd.randint(7, 14) * amt)):
        bh = rnd.randint(2, max(3, h // 18))
        y = rnd.randint(0, h - bh)
        dx = int(rnd.choice([-1, 1]) * rnd.randint(w // 60, w // 8) * min(amt, 1.5))
        band = g.crop((0, y, w, y + bh))
        out.paste(band, (dx, y))
        out.paste(band, (dx - w if dx > 0 else dx + w, y))
    # 2. smeared rows (one pixel row stretched into a band)
    for _ in range(int(rnd.randint(1, 3) * amt)):
        bh = rnd.randint(h // 60 + 1, h // 14 + 2)
        y = rnd.randint(0, h - bh - 1)
        row = out.crop((0, y, w, y + 1)).resize((w, bh))
        out.paste(row, (0, y))
    # 3. inverted / blown-out bands
    for _ in range(int(rnd.randint(1, 3) * amt)):
        bh = rnd.randint(2, h // 40 + 3)
        y = rnd.randint(0, h - bh)
        x0 = rnd.randint(0, w // 2)
        x1 = rnd.randint(x0 + w // 6, w)
        box = (x0, y, x1, y + bh)
        band = out.crop(box)
        band = ImageOps.invert(band) if rnd.random() < .5 else band.point(lambda v: 255 if v > 90 else v // 3)
        out.paste(band, box[:2])
    # 4. coarse pixel block
    if rnd.random() < .7 * amt:
        bw, bh = rnd.randint(w // 6, w // 2), rnd.randint(h // 20, h // 7)
        x, y = rnd.randint(0, w - bw), rnd.randint(0, h - bh)
        blk = out.crop((x, y, x + bw, y + bh))
        f = rnd.choice([8, 12, 16])
        blk = blk.resize((max(1, bw // f), max(1, bh // f)), Image.BILINEAR).resize((bw, bh), Image.NEAREST)
        out.paste(blk, (x, y))
    return out


def cover_images(src, dst_dir):
    """Colour thumbnail + glitched black & white thumbnail for the front page."""
    if not HAVE_PIL:
        return None
    c_thumb = cache_path(src, "thumb", ".jpg")
    c_glitch = cache_path(src, "glitch", ".jpg")
    if not (c_thumb.exists() and c_glitch.exists()):
        CACHE.mkdir(exist_ok=True)
        with Image.open(src) as im:
            rgb = representative_frame(im)
        t = rgb.copy()
        t.thumbnail((THUMB_WIDTH, THUMB_WIDTH * 3), Image.LANCZOS)
        t.save(c_thumb, quality=75, optimize=True, progressive=True)
        glitch(t, file_hash(src)).save(c_glitch, quality=72, optimize=True, progressive=True)
    shutil.copy2(c_thumb, dst_dir / "cover.jpg")
    shutil.copy2(c_glitch, dst_dir / "cover-bw.jpg")
    return {
        "thumb": "cover.jpg", "bw": "cover-bw.jpg",
        "thumb_size": image_size(dst_dir / "cover.jpg"),
        "bytes": (dst_dir / "cover-bw.jpg").stat().st_size,
    }


# ---------------------------------------------------------------- content
def load_text_file(folder):
    names = {p.name.lower(): p for p in folder.iterdir() if p.is_file()}
    for n in TEXT_NAMES:
        if n in names:
            return names[n].read_text(encoding="utf-8", errors="replace")
    others = sorted([p for p in folder.iterdir() if p.suffix.lower() in (".md", ".txt")], key=natural_key)
    return others[0].read_text(encoding="utf-8", errors="replace") if others else ""


def collect_projects():
    projects = []
    if not PROJECTS.exists():
        return projects
    for folder in sorted(PROJECTS.iterdir(), key=natural_key):
        if not folder.is_dir() or folder.name.startswith((".", "_")):
            continue
        meta, body = split_front_matter(load_text_file(folder))
        if meta.get("hidden", "").lower() in ("yes", "true", "1"):
            continue
        files = sorted([p for p in folder.iterdir() if p.is_file() and not p.name.startswith(".")],
                       key=natural_key)
        media = [p for p in files if p.suffix.lower() in IMAGE_EXT | VIDEO_EXT]
        docs = [p for p in files if p.suffix.lower() in FILE_EXT]
        images = [p for p in media if p.suffix.lower() in IMAGE_EXT]
        cover = meta.get("cover")
        cover_src = next((p for p in images if cover and p.name == cover), None) \
            or next((p for p in images if p.stem.lower() == "cover"), None) \
            or (images[0] if images else None)
        # a file called cover.* is only used as thumbnail, not shown twice
        if cover_src is not None and cover_src.stem.lower() == "cover" and len(images) > 1:
            media = [p for p in media if p != cover_src]
        title = nfc(folder.name)
        projects.append({
            "title": title,
            "slug": slugify(title),
            "folder": folder,
            "meta": meta,
            "body": body,
            "media": media,
            "docs": docs,
            "cover_src": cover_src,
            "year": meta.get("year", ""),
        })

    def sort_key(p):
        order = p["meta"].get("order")
        try:
            o = float(order)
        except (TypeError, ValueError):
            o = None
        return (o is None, o or 0, -first_year(p["year"]), p["title"].lower())

    projects.sort(key=sort_key)
    seen = {}
    for p in projects:  # unique slugs
        n = seen.get(p["slug"], 0)
        seen[p["slug"]] = n + 1
        if n:
            p["slug"] = f"{p['slug']}-{n + 1}"
    return projects


def collect_pages():
    pages = []
    if not PAGES.exists():
        return pages, None
    intro = None
    for f in sorted(PAGES.glob("*.md"), key=natural_key):
        meta, body = split_front_matter(f.read_text(encoding="utf-8"))
        if f.stem.lower() in ("index", "home"):
            intro = (meta, body)
            continue
        pages.append({
            "slug": slugify(f.stem),
            "title": meta.get("title", f.stem),
            "meta": meta,
            "body": body,
            "nav": meta.get("nav", "no").lower() in ("yes", "true", "1"),
            "order": float(meta.get("order", 99)),
        })
    pages.sort(key=lambda p: (p["order"], p["slug"]))
    return pages, intro


# ---------------------------------------------------------------- rendering
BASE_TEMPLATE = None


def render(context):
    out = BASE_TEMPLATE
    for k, v in context.items():
        out = out.replace("{{" + k + "}}", str(v))
    return re.sub(r"\{\{\w+\}\}", "", out)


def nav_html(pages, current):
    links = [("Work", f"{SITE['base']}/", current == "work")]
    links += [(p["title"], f"{SITE['base']}/{p['slug']}/", current == p["slug"]) for p in pages if p["nav"]]
    cur = ' aria-current="page"'
    return "".join(f'<a href="{u}"{cur if active else ""}>{esc(t)}</a>' for t, u, active in links)


def footer_nav_html(pages):
    return "".join(f'<a href="{SITE["base"]}/{p["slug"]}/">{esc(p["title"])}</a>'
                   for p in pages if not p["nav"])


ASSET_BYTES = 0


def canonical_url(path):
    rel = path.relative_to(OUT).parent.as_posix()
    return SITE["url"].rstrip("/") + "/" + ("" if rel == "." else rel + "/")


def page(path, *, title, content, pages, current, body_class="", description=None,
         media_bytes=0, og_image=""):
    full_title = SITE["name"] if not title else f"{title} · {SITE['name']}"
    ctx = {
        "lang": SITE["lang"],
        "base": SITE["base"],
        "page_title": esc(full_title),
        "description": esc(description or SITE["description"]),
        "og_title": esc(title or SITE["name"]),
        "og_image": og_image,
        "canonical": canonical_url(path),
        "nav": nav_html(pages, current),
        "footer_nav": footer_nav_html(pages),
        "content": content,
        "body_class": body_class,
        "year": date.today().year,
        "site_name": esc(SITE["name"]),
        "version": CACHE_VERSION + str(int(os.environ.get("GITHUB_RUN_NUMBER", "0"))),
    }
    html_out = render(ctx)
    weight = len(html_out.encode()) + media_bytes + ASSET_BYTES
    html_out = html_out.replace("<!--weight-->", human_size(weight))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_out, encoding="utf-8")


def build():
    global BASE_TEMPLATE, ASSET_BYTES
    BASE_TEMPLATE = (THEME / "base.html").read_text(encoding="utf-8")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    # assets
    shutil.copytree(THEME, OUT / "assets", ignore=shutil.ignore_patterns("base.html", "*.md", ".DS_Store"))
    ASSET_BYTES = sum((OUT / "assets" / f).stat().st_size
                      for f in ("style.css", "main.js", "fonts/jbm-regular.woff2", "fonts/jbm-bold.woff2")
                      if (OUT / "assets" / f).exists())

    projects = collect_projects()
    pages, intro = collect_pages()
    b = SITE["base"]

    # ---- project pages
    for i, p in enumerate(projects):
        d = OUT / "work" / p["slug"]
        d.mkdir(parents=True)
        figures, total = [], 0
        n = len(p["media"])
        for j, src in enumerate(p["media"], 1):
            label = f"{j:02d}/{n:02d}"
            alt = esc(f"{p['title']} - {j}/{n}")
            if src.suffix.lower() in VIDEO_EXT:
                dst = d / f"{j:02d}{src.suffix.lower()}"
                shutil.copy2(src, dst)
                total += dst.stat().st_size
                figures.append(
                    f'<figure class="shot"><video src="{dst.name}" controls playsinline preload="metadata"></video>'
                    f'<figcaption><span>{label}</span></figcaption></figure>')
                continue
            dst, size = web_image(src, d, f"{j:02d}")
            p.setdefault("first_web", dst.name)
            nbytes = dst.stat().st_size
            total += nbytes
            wh = f' width="{size[0]}" height="{size[1]}"' if size else ""
            dims = f"{size[0]}×{size[1]} · " if size else ""
            loading = "eager" if j == 1 else "lazy"
            figures.append(
                f'<figure class="shot"><a href="{dst.name}"><img src="{dst.name}"{wh} alt="{alt}" loading="{loading}" decoding="async"></a>'
                f'<figcaption><span>{label}</span></figcaption></figure>')
        doc_links = []
        for src in p["docs"]:
            dst = d / slugify(src.stem)
            dst = dst.with_suffix(src.suffix.lower())
            shutil.copy2(src, dst)
            doc_links.append(f'<li><a href="{dst.name}">↓ {esc(nfc(src.name))}</a> <span class="dim">{human_size(dst.stat().st_size)}</span></li>')

        p["cover"] = cover_images(p["cover_src"], d) if p["cover_src"] else None
        p["bytes"] = total
        p["count"] = n

        subtitle = f'<p class="subtitle">{inline(p["meta"]["subtitle"])}</p>' if p["meta"].get("subtitle") else ""
        text_html = markdown(p["body"]) if p["body"].strip() else '<p class="dim">// no description yet</p>'
        if doc_links:
            text_html += f'<ul class="docs">{"".join(doc_links)}</ul>'
        prev_p = projects[i - 1] if i > 0 else projects[-1]
        next_p = projects[(i + 1) % len(projects)]
        pager = ""
        if len(projects) > 1:
            pager = (f'<nav class="pager" aria-label="more projects">'
                     f'<a href="{b}/work/{prev_p["slug"]}/" rel="prev" data-key="ArrowLeft"><span class="dim">← previous</span> {esc(prev_p["title"])}</a>'
                     f'<a href="{b}/work/{next_p["slug"]}/" rel="next" data-key="ArrowRight"><span class="dim">next →</span> {esc(next_p["title"])}</a></nav>')
        content = f"""
<article class="project">
  <p class="back"><a href="{b}/#work">← all work</a></p>
  <div class="project-grid">
    <header class="project-text">
      <h1>{esc(p['title'])}</h1>
      {subtitle}
      <div class="prose">{text_html}</div>
    </header>
    <div class="project-media">
      {''.join(figures) or '<p class="dim">// no images yet</p>'}
    </div>
  </div>
  {pager}
</article>"""
        og = f"{SITE['url'].rstrip('/')}/work/{p['slug']}/cover.jpg" if p["cover"] else ""
        page(d / "index.html", title=p["title"], content=content, pages=pages, current="work",
             body_class="is-project", description=strip_markup(p["body"]) or p["title"],
             media_bytes=total, og_image=og)

    # ---- front page
    cards = []
    for i, p in enumerate(projects, 1):
        c = p["cover"]
        if c:
            ts = c["thumb_size"]
            thumb = (f'<span class="thumb">'
                     f'<img class="bw" src="{b}/work/{p["slug"]}/{c["bw"]}" width="{ts[0]}" height="{ts[1]}" alt="" loading="lazy">'
                     f'<img class="color" data-src="{b}/work/{p["slug"]}/{c["thumb"]}" alt="" width="{ts[0]}" height="{ts[1]}">'
                     f'</span>')
        elif p.get("first_web"):
            thumb = f'<span class="thumb"><img class="plain" src="{b}/work/{p["slug"]}/{p["first_web"]}" alt="" loading="lazy"></span>'
        else:
            thumb = '<span class="thumb empty"><span>no signal</span></span>'
        cards.append(f"""
  <li class="card">
    <a href="{b}/work/{p['slug']}/">
      {thumb}
      <span class="meta"><span class="title">{esc(p['title'])}</span><span class="year">{esc(p['year'])}</span></span>
    </a>
  </li>""")
    intro_html = markdown(intro[1]) if intro and intro[1].strip() else ""
    home = f"""
<section class="intro">
  <div class="prose">{intro_html}</div>
</section>
<h2 class="section-label" id="work">Work <span class="dim">({len(projects)})</span></h2>
<ol class="grid">{''.join(cards)}
</ol>"""
    index_media = sum((p["cover"] or {}).get("bytes", 0) for p in projects)
    page(OUT / "index.html", title="", content=home, pages=pages, current="work",
         body_class="is-home", media_bytes=index_media,
         og_image=f"{SITE['url'].rstrip('/')}/work/{projects[0]['slug']}/cover.jpg" if projects and projects[0]["cover"] else "")

    # ---- simple pages (about, impressum, ...)
    for pg in pages:
        content = f"""
<article class="page">
  <h1>{esc(pg['title'])}</h1>
  <div class="prose">{markdown(pg['body'])}</div>
</article>"""
        page(OUT / pg["slug"] / "index.html", title=pg["title"], content=content, pages=pages,
             current=pg["slug"], body_class="is-page")

    # ---- 404 + redirects from the old site + extras
    page(OUT / "404.html", title="404", pages=pages, current="", body_class="is-page",
         content=f'<article class="page"><h1>404</h1><div class="prose"><p>This page does not exist (anymore).</p>'
                 f'<p><a href="{b}/">← back to work</a></p></div></article>')
    about = next((pg for pg in pages if pg["slug"] in ("about", "bio", "biographie")), None)
    old = {"projects.html": "/", "about.html": f"/{about['slug']}/" if about else "/",
           "aboutMe.html": f"/{about['slug']}/" if about else "/"}
    dviw = next((p for p in projects if p["slug"].startswith("das-vergessen")), None)
    if dviw:
        old["dviw.html"] = f"/work/{dviw['slug']}/"
    for name, target in old.items():
        (OUT / name).write_text(
            f'<!doctype html><meta charset="utf-8"><title>moved</title>'
            f'<meta http-equiv="refresh" content="0; url={b}{target}">'
            f'<link rel="canonical" href="{b}{target}"><a href="{b}{target}">moved here</a>', encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    if (ROOT / "CNAME").exists():
        shutil.copy2(ROOT / "CNAME", OUT / "CNAME")
    urls = ["/"] + [f"/work/{p['slug']}/" for p in projects] + [f"/{pg['slug']}/" for pg in pages]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE['url'].rstrip('/')}{u}</loc></url>\n" for u in urls) + "</urlset>\n",
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['url'].rstrip('/')}/sitemap.xml\n")

    print(f"built {len(projects)} projects, {len(pages)} pages -> {OUT}")
    if not HAVE_PIL:
        print("\n" + "!" * 64 +
              "\n  Pillow is not installed, so this LOCAL preview has no glitch\n"
              "  thumbnails and images are not resized. (The real site built\n"
              "  on GitHub is fine.) To fix the preview, run:\n\n"
              "      python3 -m pip install --user pillow\n\n"
              "  then build again.\n" + "!" * 64 + "\n")
    for p in projects:
        print(f"  {p['slug']:<40} {p['count']:>3} files  {human_size(p['bytes']):>8}")


def serve():
    import functools
    import http.server
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    port = int(os.environ.get("PORT", 8000))
    print(f"preview: http://localhost:{port}   (ctrl+c to stop)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        try:
            serve()
        except KeyboardInterrupt:
            pass
