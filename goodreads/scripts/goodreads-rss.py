#!/usr/bin/env python3
"""
Goodreads RSS Reader — for OpenClaw agents
Usage:
  python3 goodreads-rss.py shelf   <user_id> [--shelf read|currently-reading|to-read|<custom>] [--limit N] [--sort date_read|date_added|rating|title|avg_rating]
  python3 goodreads-rss.py book    <book_id>
  python3 goodreads-rss.py reviews <book_id> [--limit N]
  python3 goodreads-rss.py activity <user_id> [--limit N]
  python3 goodreads-rss.py search  <query> [--limit N]
"""

import sys
import argparse
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import html
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def fetch_url(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def clean_ws(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"]:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except Exception:
            pass
    return date_str


# ── SHELF ──────────────────────────────────────────────────────────────────────
def cmd_shelf(args):
    shelf = args.shelf or "read"
    limit = min(args.limit or 20, 200)
    sort = args.sort or "date_added"
    url = (
        f"https://www.goodreads.com/review/list_rss/{args.user_id}"
        f"?shelf={urllib.parse.quote(shelf)}&per_page={limit}&sort={sort}&order=d"
    )
    xml = fetch_url(url)
    root = ET.fromstring(xml)
    channel = root.find("channel")

    # Meta
    user_name = (channel.findtext("title") or "").replace(f"'s bookshelf: {shelf}", "").strip()

    books = []
    for item in channel.findall("item"):
        books.append({
            "title":          item.findtext("title"),
            "author":         item.findtext("author_name"),
            "book_id":        item.findtext("book_id"),
            "isbn":           item.findtext("isbn"),
            "user_rating":    item.findtext("user_rating"),   # 0 = chưa rate
            "average_rating": item.findtext("average_rating"),
            "date_read":      parse_date(item.findtext("user_read_at")),
            "date_added":     parse_date(item.findtext("user_date_added")),
            "review":         strip_html(item.findtext("user_review")),
            "shelves":        item.findtext("user_shelves"),
            "book_url":       f"https://www.goodreads.com/book/show/{item.findtext('book_id')}",
            "review_url":     item.findtext("link"),
            "description":    strip_html(item.findtext("book_description") or "")[:300],
            "published":      item.findtext("book_published"),
        })

    print(json.dumps({
        "user_id":   args.user_id,
        "user_name": user_name,
        "shelf":     shelf,
        "count":     len(books),
        "books":     books,
    }, ensure_ascii=False, indent=2))


# ── ACTIVITY ───────────────────────────────────────────────────────────────────
def cmd_activity(args):
    limit = args.limit or 20
    url = f"https://www.goodreads.com/user/updates_rss/{args.user_id}"
    xml = fetch_url(url)
    root = ET.fromstring(xml)
    channel = root.find("channel")

    events = []
    for item in list(channel.findall("item"))[:limit]:
        events.append({
            "title":   clean_ws(item.findtext("title") or ""),
            "date":    parse_date(item.findtext("pubDate")),
            "link":    item.findtext("link"),
            "summary": clean_ws(strip_html(item.findtext("description") or ""))[:300],
        })

    print(json.dumps({
        "user_id": args.user_id,
        "count":   len(events),
        "events":  events,
    }, ensure_ascii=False, indent=2))


# ── BOOK INFO ──────────────────────────────────────────────────────────────────
def cmd_book(args):
    """Scrape trang book để lấy thông tin chi tiết"""
    url = f"https://www.goodreads.com/book/show/{args.book_id}"
    page_html = fetch_url(url)

    # Tìm JSON-LD schema
    schema_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', page_html, re.DOTALL)
    data = {}
    if schema_match:
        try:
            data = json.loads(schema_match.group(1))
        except Exception:
            pass

    # Tìm rating count từ HTML
    rating_count_match = re.search(r'"ratingCount"\s*:\s*(\d+)', page_html)
    reviews_count_match = re.search(r'"reviewCount"\s*:\s*(\d+)', page_html)

    # Fallback scrape nếu JSON-LD thiếu
    title = html.unescape(data.get("name") or "")
    if not title:
        t = re.search(r'<title>([^|<]+)', page_html)
        title = t.group(1).strip() if t else ""

    desc = strip_html(data.get("description", ""))
    if not desc:
        desc_match = re.search(r'"description"\s*:\s*"((?:[^"\\]|\\.){20,})"', page_html)
        if desc_match:
            desc = html.unescape(desc_match.group(1).replace("\\n", " ").replace('\\"', '"'))

    result = {
        "book_id":        args.book_id,
        "title":          clean_ws(title),
        "author":         data.get("author", [{}])[0].get("name") if isinstance(data.get("author"), list) else (data.get("author") or {}).get("name"),
        "average_rating": data.get("aggregateRating", {}).get("ratingValue"),
        "rating_count":   rating_count_match.group(1) if rating_count_match else None,
        "review_count":   reviews_count_match.group(1) if reviews_count_match else None,
        "description":    clean_ws(desc)[:500],
        "isbn":           data.get("isbn"),
        "published":      data.get("datePublished"),
        "genres":         data.get("genre", []),
        "book_url":       f"https://www.goodreads.com/book/show/{args.book_id}",
        "image_url":      data.get("image"),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


# ── REVIEWS ────────────────────────────────────────────────────────────────────
def cmd_reviews(args):
    """Scrape reviews của 1 cuốn sách từ trang book (RSS đã bị Goodreads remove)"""
    limit = args.limit or 10
    url = f"https://www.goodreads.com/book/show/{args.book_id}"
    html_content = fetch_url(url)

    # Lấy title
    title_match = re.search(r'<title>([^|<]+)', html_content)
    book_title = title_match.group(1).strip() if title_match else args.book_id

    # Parse JSON-LD để lấy rating tổng
    schema_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_content, re.DOTALL)
    avg_rating = None
    if schema_match:
        try:
            schema = json.loads(schema_match.group(1))
            avg_rating = schema.get("aggregateRating", {}).get("ratingValue")
        except Exception:
            pass

    # Scrape review snippets từ HTML
    reviews = []
    review_blocks = re.findall(
        r'"reviewBody"\s*:\s*"((?:[^"\\]|\\.)*)".*?"ratingValue"\s*:\s*(\d)',
        html_content, re.DOTALL
    )
    for i, (body, rating) in enumerate(review_blocks[:limit]):
        reviews.append({
            "rating": int(rating),
            "review": html.unescape(body.replace("\\n", " ").replace('\\"', '"'))[:400],
        })

    # Fallback: tìm rating distribution
    rating_dist = {}
    dist_matches = re.findall(r'"ratingCount"\s*:\s*(\d+).*?"bestRating"\s*:\s*"(\d)"', html_content)

    print(json.dumps({
        "book_id":      args.book_id,
        "book_title":   clean_ws(book_title),
        "average_rating": avg_rating,
        "review_count": len(reviews),
        "note":         "Top reviews scraped từ book page. Goodreads đã remove RSS reviews endpoint.",
        "reviews":      reviews,
    }, ensure_ascii=False, indent=2))


# ── SEARCH ─────────────────────────────────────────────────────────────────────
def cmd_search(args):
    """Tìm kiếm sách trên Goodreads"""
    limit = args.limit or 10
    q = urllib.parse.quote(args.query)
    url = f"https://www.goodreads.com/search?q={q}&search_type=books"
    html_content = fetch_url(url)

    # Parse kết quả tìm kiếm
    books = []
    # Tìm các block sách trong kết quả
    pattern = re.findall(
        r'href="/book/show/(\d+)[^"]*"[^>]*>\s*<img[^>]+alt="([^"]+)".*?'
        r'class="authorName"[^>]*>[^<]*<span[^>]*>([^<]+)</span>',
        html_content, re.DOTALL
    )

    seen = set()
    for match in pattern:
        book_id, title, author = match
        if book_id not in seen and len(books) < limit:
            seen.add(book_id)
            books.append({
                "book_id":  book_id,
                "title":    html.unescape(title.strip()),
                "author":   html.unescape(author.strip()),
                "book_url": f"https://www.goodreads.com/book/show/{book_id}",
            })

    # Fallback: tìm book IDs từ search result page
    if not books:
        ids = re.findall(r'/book/show/(\d+)', html_content)
        titles = re.findall(r'class="bookTitle"[^>]*>\s*<span[^>]*>([^<]+)</span>', html_content)
        authors = re.findall(r'class="authorName"[^>]*>[^<]*<span[^>]*>([^<]+)</span>', html_content)
        seen = set()
        for i, book_id in enumerate(ids):
            if book_id not in seen and len(books) < limit:
                seen.add(book_id)
                books.append({
                    "book_id":  book_id,
                    "title":    html.unescape(titles[i].strip()) if i < len(titles) else None,
                    "author":   html.unescape(authors[i].strip()) if i < len(authors) else None,
                    "book_url": f"https://www.goodreads.com/book/show/{book_id}",
                })

    print(json.dumps({
        "query": args.query,
        "count": len(books),
        "books": books,
    }, ensure_ascii=False, indent=2))


# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Goodreads RSS/Scrape Tool for OpenClaw")
    sub = parser.add_subparsers(dest="cmd")

    # shelf
    p_shelf = sub.add_parser("shelf", help="Lấy danh sách sách từ shelf của user")
    p_shelf.add_argument("user_id")
    p_shelf.add_argument("--shelf", default="read", help="read|currently-reading|to-read|<custom>")
    p_shelf.add_argument("--limit", type=int, default=20)
    p_shelf.add_argument("--sort", default="date_added", help="date_read|date_added|rating|title|avg_rating")

    # activity
    p_act = sub.add_parser("activity", help="Xem hoạt động gần nhất của user")
    p_act.add_argument("user_id")
    p_act.add_argument("--limit", type=int, default=20)

    # book
    p_book = sub.add_parser("book", help="Thông tin chi tiết 1 cuốn sách")
    p_book.add_argument("book_id")

    # reviews
    p_rev = sub.add_parser("reviews", help="Lấy reviews của 1 cuốn sách")
    p_rev.add_argument("book_id")
    p_rev.add_argument("--limit", type=int, default=20)

    # search
    p_search = sub.add_parser("search", help="Tìm kiếm sách theo tên/tác giả")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    try:
        {"shelf": cmd_shelf, "activity": cmd_activity, "book": cmd_book,
         "reviews": cmd_reviews, "search": cmd_search}[args.cmd](args)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
