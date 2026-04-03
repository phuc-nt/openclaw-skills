#!/usr/bin/env python3
"""
Goodreads Writer — Browser automation via Playwright for OpenClaw agents
Cho phép: rate, review, đổi shelf, start/finish reading, update progress.

Yêu cầu:
  - Playwright + Chromium: ~/.openclaw/common-scripts/.venv/
  - Login lần đầu: python3 goodreads-writer.py login
  - Sau đó dùng các command khác (persistent cookie session)

Usage:
  python3 goodreads-writer.py login
  python3 goodreads-writer.py rate    <book_id> <stars>
  python3 goodreads-writer.py shelf   <book_id> <shelf_name>
  python3 goodreads-writer.py review  <book_id> "<text>"
  python3 goodreads-writer.py start   <book_id>
  python3 goodreads-writer.py finish  <book_id>
  python3 goodreads-writer.py progress <book_id> <page_or_percent>
  python3 goodreads-writer.py status
"""

import sys
import os
import json
import argparse
import asyncio
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────────
GOODREADS_BASE = "https://www.goodreads.com"
# Persistent browser data — stores cookies/session across runs
SCRIPT_DIR = Path(__file__).parent
USER_DATA_DIR = str(SCRIPT_DIR / ".browser-data")
# Timeout for page operations (ms)
DEFAULT_TIMEOUT = 15000
NAVIGATION_TIMEOUT = 30000


def result_json(success: bool, action: str, **kwargs):
    """Print JSON result and exit."""
    data = {"success": success, "action": action, **kwargs}
    print(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(0 if success else 1)


async def create_browser_context(playwright, headless=True):
    """Create a persistent browser context with stealth mode to bypass anti-bot."""
    Path(USER_DATA_DIR).mkdir(parents=True, exist_ok=True)
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=headless,
        viewport={"width": 1280, "height": 800},
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        locale="en-US",
        timezone_id="America/New_York",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ],
        ignore_default_args=["--enable-automation"],
    )
    context.set_default_timeout(DEFAULT_TIMEOUT)
    context.set_default_navigation_timeout(NAVIGATION_TIMEOUT)

    # Apply stealth to bypass anti-bot detection
    try:
        from playwright_stealth import stealth_async
        for page in context.pages:
            await stealth_async(page)
        # Also apply stealth to future pages
        context.on("page", lambda page: asyncio.ensure_future(stealth_async(page)))
    except ImportError:
        pass  # stealth not installed, continue without it

    return context


async def check_page_blocked(page) -> bool:
    """Check if page got 403/blocked by anti-bot."""
    title = await page.title()
    if "403" in title or "Forbidden" in title or "blocked" in title.lower():
        return True
    body = await page.text_content("body") or ""
    if "403 Forbidden" in body or "Access Denied" in body:
        return True
    return False


async def check_logged_in(page) -> bool:
    """Check if current session is logged in to Goodreads."""
    await page.goto(GOODREADS_BASE, wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)  # Wait for React to render

    # Check URL — if redirected to sign_in, definitely not logged in
    if "sign_in" in page.url or "sign_up" in page.url:
        return False

    # Check for logged-in indicators (multiple selectors for robustness)
    try:
        await page.wait_for_selector(
            'a[href*="/review/list"], '
            '.dropdown--profileMenu, '
            'nav a[href*="my_books"], '
            'a[href*="/user/show"], '
            'button[aria-label*="Profile"]',
            timeout=8000
        )
        return True
    except Exception:
        pass

    # Final check — look for sign-in link (means NOT logged in)
    sign_in = await page.query_selector('a[href*="sign_in"], a:has-text("Sign in")')
    if sign_in:
        return False

    # Ambiguous — safer to say not logged in
    return False


def verify_shelf_rss(user_id: str, book_id: str, expected_shelf: str) -> bool:
    """Verify book is on the expected shelf via RSS (read-only check)."""
    import urllib.request
    import xml.etree.ElementTree as ET
    url = (
        f"https://www.goodreads.com/review/list_rss/{user_id}"
        f"?shelf={expected_shelf}&per_page=50&sort=date_added&order=d"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            xml_data = r.read().decode("utf-8")
        root = ET.fromstring(xml_data)
        for item in root.findall(".//item"):
            bid = item.findtext("book_id")
            if bid == str(book_id):
                return True
    except Exception:
        pass
    return False


async def navigate_to_book(page, book_id: str):
    """Navigate to a book page and wait for it to load."""
    url = f"{GOODREADS_BASE}/book/show/{book_id}"
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)  # Wait for React

    # Check if redirected to sign_in (session expired mid-operation)
    if "sign_in" in page.url or "sign_up" in page.url:
        raise Exception("Session expired. Run: goodreads-writer.py login")

    # Wait for the book title to appear
    try:
        await page.wait_for_selector(
            'h1[data-testid="bookTitle"], h1.Text__title1',
            timeout=10000
        )
    except Exception:
        # Fallback — just wait for any h1
        await page.wait_for_selector("h1", timeout=5000)


# ── LOGIN ──────────────────────────────────────────────────────────────────────
async def cmd_login(args):
    """
    Login interactivo — mở browser có giao diện để user đăng nhập thủ công.
    Sau khi đăng nhập xong, cookie sẽ được lưu vào persistent context.
    """
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        # headless=False để user thấy browser và đăng nhập
        context = await create_browser_context(p, headless=False)
        page = context.pages[0] if context.pages else await context.new_page()

        # Navigate to Goodreads sign-in page (will show Amazon/Apple/Email options)
        await page.goto(
            f"{GOODREADS_BASE}/user/sign_in",
            wait_until="domcontentloaded"
        )

        print("🔐 Browser opened for Goodreads login.")
        print("   Choose 'Continue with Amazon' or email to sign in.")
        print("   After signing in and seeing the Goodreads homepage,")
        print("   return to this terminal and press Enter to save session.")
        print()

        # Wait for user to press Enter
        input(">>> Press Enter after successful login... ")

        # Verify login
        logged_in = await check_logged_in(page)
        await context.close()

        if logged_in:
            result_json(True, "login", message="Login successful! Session saved.")
        else:
            result_json(False, "login", error="Login not detected. Please try again.")


# ── STATUS ─────────────────────────────────────────────────────────────────────
async def cmd_status(args):
    """Check login status."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        context = await create_browser_context(p, headless=True)
        page = context.pages[0] if context.pages else await context.new_page()
        logged_in = await check_logged_in(page)
        await context.close()

        if logged_in:
            result_json(True, "status", message="Session active — logged into Goodreads.")
        else:
            result_json(False, "status",
                        error="Not logged in or session expired. Run: goodreads-writer.py login")


# ── RATE ───────────────────────────────────────────────────────────────────────
async def cmd_rate(args):
    """Rate a book 1-5 stars."""
    stars = int(args.stars)
    if not 1 <= stars <= 5:
        result_json(False, "rate", error="Stars phải từ 1 đến 5")

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        context = await create_browser_context(p, headless=True)
        page = context.pages[0] if context.pages else await context.new_page()

        if not await check_logged_in(page):
            await context.close()
            result_json(False, "rate", error="Not logged in. Run: goodreads-writer.py login")

        await navigate_to_book(page, args.book_id)

        # Get book title for confirmation
        title = await page.text_content('h1[data-testid="bookTitle"], h1.Text__title1') or args.book_id

        # Click the star rating button
        # Goodreads uses buttons with aria-label like "Rate N out of 5"
        star_selector = f'button[aria-label="Rate {stars} out of 5"]'
        try:
            # Try sidebar rating first
            star_buttons = await page.query_selector_all(star_selector)
            if star_buttons:
                await star_buttons[0].click()
                await page.wait_for_timeout(2000)  # Wait for rating to register

                await context.close()
                result_json(True, "rate", book_id=args.book_id, title=title.strip(),
                            stars=stars, message=f"Đã rate {stars} sao cho '{title.strip()}'")
            else:
                await context.close()
                result_json(False, "rate", error=f"Không tìm thấy nút rating. Selector: {star_selector}")
        except Exception as e:
            await context.close()
            result_json(False, "rate", error=str(e))


# ── SHELF ──────────────────────────────────────────────────────────────────────
# Overlay buttons use these exact aria-labels (lowercase!):
SHELF_ARIA = {
    "read": "Read",
    "currently-reading": "Currently reading",
    "to-read": "Want to read",
    "want-to-read": "Want to read",
}
# User ID for RSS verification — set via environment variable or pass as argument
GOODREADS_USER_ID = os.environ.get("GOODREADS_USER_ID", "")


async def _click_shelf_in_overlay(page, target_aria: str) -> bool:
    """Click shelf option inside the WTRStepShelving overlay. Returns True if clicked."""
    # Wait for the overlay dialog to appear
    try:
        await page.wait_for_selector('[role="dialog"], .Overlay--floating', timeout=3000)
    except Exception:
        return False

    # Find the button by exact aria-label
    btn = await page.query_selector(f'button[aria-label="{target_aria}"]')
    if btn:
        await btn.click()
        await page.wait_for_timeout(2000)

        # The overlay might show a second page (dates, etc.) — dismiss it
        try:
            close_btn = await page.query_selector('.Overlay button[aria-label="Close"]')
            if close_btn:
                is_visible = await close_btn.is_visible()
                if is_visible:
                    await close_btn.click()
                    await page.wait_for_timeout(1000)
        except Exception:
            pass

        return True
    return False


async def cmd_shelf(args):
    """Move book to a shelf: read, currently-reading, to-read, or custom."""
    shelf_name = args.shelf_name.lower().replace(" ", "-")
    target_aria = SHELF_ARIA.get(shelf_name)
    if not target_aria:
        result_json(False, "shelf", error=f"Unknown shelf: {shelf_name}. Use: read, currently-reading, to-read")

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        context = await create_browser_context(p, headless=True)
        page = context.pages[0] if context.pages else await context.new_page()

        if not await check_logged_in(page):
            await context.close()
            result_json(False, "shelf", error="Not logged in. Run: goodreads-writer.py login")

        await navigate_to_book(page, args.book_id)
        title = await page.text_content('h1[data-testid="bookTitle"], h1.Text__title1') or args.book_id

        try:
            # Step 1: Click the dropdown/caret to open shelf overlay
            # When unshelved: aria="Tap to choose a shelf for this book"
            # When already shelved: aria="Shelved as 'X'. Tap to edit shelf for this book"
            dropdown_btn = await page.query_selector(
                'button[aria-label="Tap to choose a shelf for this book"]'
            )
            if not dropdown_btn:
                dropdown_btn = await page.query_selector(
                    'button[aria-label*="Tap to edit shelf for this book"]'
                )

            if dropdown_btn:
                # Book already on a shelf — just click dropdown to change
                await dropdown_btn.click()
                await page.wait_for_timeout(1500)
                success = await _click_shelf_in_overlay(page, target_aria)
            else:
                # Book not shelved yet — need to open overlay via "Want to Read" dropdown
                # But first check: is there a "Want to Read" button?
                want_btn = await page.query_selector(
                    'button[aria-label="Tap to shelve book as want to read"]'
                )
                if not want_btn:
                    await context.close()
                    result_json(False, "shelf", error="Không tìm thấy nút shelf trên trang sách.")

                if shelf_name in ("to-read", "want-to-read"):
                    # Just click Want to Read directly
                    await want_btn.click()
                    await page.wait_for_timeout(2000)
                    # Dismiss any overlay that pops up
                    try:
                        close_btn = await page.query_selector('.Overlay button[aria-label="Close"]')
                        if close_btn and await close_btn.is_visible():
                            await close_btn.click()
                    except Exception:
                        pass
                    success = True
                else:
                    # Need to shelve first, then change to target shelf
                    # Click the dropdown (caret) next to Want to Read to get overlay directly
                    # The caret is the sibling button
                    caret = await page.query_selector(
                        'button[aria-label="Tap to choose a shelf for this book"]'
                    )
                    if not caret:
                        caret = await page.query_selector(
                            'button[aria-label*="Tap to edit shelf for this book"]'
                        )
                    if not caret:
                        # If no caret, click Want to Read first, wait, then find caret
                        await want_btn.click()
                        await page.wait_for_timeout(2000)
                        # Dismiss any overlay
                        try:
                            close_btn = await page.query_selector('.Overlay button[aria-label="Close"]')
                            if close_btn and await close_btn.is_visible():
                                await close_btn.click()
                                await page.wait_for_timeout(1000)
                        except Exception:
                            pass
                        # Now find the caret/dropdown
                        caret = await page.query_selector(
                            'button[aria-label="Tap to choose a shelf for this book"]'
                        )
                        if not caret:
                            caret = await page.query_selector(
                                'button[aria-label*="Tap to edit shelf for this book"]'
                            )

                    if caret:
                        await caret.click()
                        await page.wait_for_timeout(1500)
                        success = await _click_shelf_in_overlay(page, target_aria)
                    else:
                        success = False

            # Verify via RSS
            display_name = {"read": "Read", "currently-reading": "Currently Reading",
                            "to-read": "Want to Read"}.get(shelf_name, shelf_name)

            if success:
                # Give Goodreads a moment to update
                await page.wait_for_timeout(2000)
                verified = verify_shelf_rss(GOODREADS_USER_ID, args.book_id, shelf_name)
                await context.close()
                if verified:
                    result_json(True, "shelf", book_id=args.book_id, title=title.strip(),
                                shelf=shelf_name, verified=True,
                                message=f"✅ Đã chuyển '{title.strip()}' sang shelf '{display_name}' (RSS verified)")
                else:
                    result_json(True, "shelf", book_id=args.book_id, title=title.strip(),
                                shelf=shelf_name, verified=False,
                                message=f"⚠️ Đã click shelf '{display_name}' nhưng chưa xác nhận được qua RSS (có thể cần vài phút)")
            else:
                await context.close()
                result_json(False, "shelf", book_id=args.book_id,
                            error=f"Không tìm thấy option '{target_aria}' trong overlay.")

        except Exception as e:
            await context.close()
            result_json(False, "shelf", error=str(e))


# ── EDIT (dates, review, rating) ───────────────────────────────────────────────
async def _navigate_to_edit_page(page, book_id: str):
    """Navigate to /review/edit/<book_id> and verify the page loads.

    Goodreads may redirect:
      - /review/edit/<id> → for books with existing reviews
      - /review/new/<id>  → for books shelved but no review yet
    Both are valid review form pages.
    """
    url = f"{GOODREADS_BASE}/review/edit/{book_id}"
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)

    if "sign_in" in page.url or "sign_up" in page.url:
        raise Exception("Session expired. Run: goodreads-writer.py login")

    # Verify it's a review form page (edit or new)
    current_url = page.url
    is_review_page = "/review/edit" in current_url or "/review/new" in current_url
    if not is_review_page:
        title = await page.title()
        if "Review" not in title and "review" not in current_url:
            raise Exception(f"Cannot access edit page. Book not shelved? URL: {current_url}")


async def cmd_edit(args):
    """Edit reading dates, review text, and/or re-rate a book on the /review/edit/ page."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        context = await create_browser_context(p, headless=True)
        page = context.pages[0] if context.pages else await context.new_page()

        try:
            # _navigate_to_edit_page already checks for sign_in redirect
            await _navigate_to_edit_page(page, args.book_id)

            changes = []

            # Edit start date (YYYY-MM-DD)
            if hasattr(args, 'start_date') and args.start_date:
                parts = args.start_date.split("-")
                if len(parts) == 3:
                    y, m, d = parts
                    # Find the date selects by name pattern
                    year_sel = await page.query_selector('select[name*="[start][year]"]')
                    month_sel = await page.query_selector('select[name*="[start][month]"]')
                    day_sel = await page.query_selector('select[name*="[start][day]"]')
                    if year_sel and month_sel and day_sel:
                        await year_sel.select_option(value=y)
                        await month_sel.select_option(value=str(int(m)))  # Remove leading zero
                        await day_sel.select_option(value=str(int(d)))
                        changes.append(f"start_date={args.start_date}")
                    else:
                        changes.append("start_date=FAILED (selects not found)")

            # Edit end date (YYYY-MM-DD)
            if hasattr(args, 'end_date') and args.end_date:
                parts = args.end_date.split("-")
                if len(parts) == 3:
                    y, m, d = parts
                    year_sel = await page.query_selector('select[name*="[end][year]"]')
                    month_sel = await page.query_selector('select[name*="[end][month]"]')
                    day_sel = await page.query_selector('select[name*="[end][day]"]')
                    if year_sel and month_sel and day_sel:
                        await year_sel.select_option(value=y)
                        await month_sel.select_option(value=str(int(m)))
                        await day_sel.select_option(value=str(int(d)))
                        changes.append(f"end_date={args.end_date}")
                    else:
                        changes.append("end_date=FAILED (selects not found)")

            # Edit review text
            if hasattr(args, 'review') and args.review:
                textarea = await page.query_selector('textarea[name="review[review]"]')
                if not textarea:
                    textarea = await page.query_selector('#review_review_usertext')
                if textarea:
                    await textarea.fill("")
                    await textarea.fill(args.review)
                    changes.append(f"review={args.review[:50]}...")
                else:
                    changes.append("review=FAILED (textarea not found)")

            # Edit star rating
            if hasattr(args, 'stars') and args.stars:
                stars = int(args.stars)
                # On edit page, stars are radio buttons or star elements
                star_btn = await page.query_selector(f'button[aria-label="Rate {stars} out of 5"]')
                if not star_btn:
                    # Try radio buttons: review[rating]
                    star_btn = await page.query_selector(f'input[name="review[rating]"][value="{stars}"]')
                if star_btn:
                    await star_btn.click()
                    changes.append(f"stars={stars}")
                else:
                    # Try clicking star by class
                    star_labels = await page.query_selector_all('.star')
                    if len(star_labels) >= stars:
                        await star_labels[stars - 1].click()
                        changes.append(f"stars={stars}")
                    else:
                        changes.append("stars=FAILED (star element not found)")

            if not changes:
                await context.close()
                result_json(False, "edit", error="Không có gì để edit. Cần ít nhất --start-date, --end-date, --review, hoặc --stars")

            # Submit the form
            save_btn = await page.query_selector(f'input#review_submit_for_{args.book_id}')
            if not save_btn:
                save_btn = await page.query_selector('input[type="submit"][value="Save"]')
            if not save_btn:
                save_btn = await page.query_selector('input[type="submit"]')

            if save_btn:
                await save_btn.click()
                await page.wait_for_timeout(3000)

                await context.close()
                result_json(True, "edit", book_id=args.book_id,
                            changes=changes,
                            message=f"✅ Đã cập nhật: {', '.join(changes)}")
            else:
                await context.close()
                result_json(False, "edit", error="Không tìm thấy nút Save.")

        except Exception as e:
            await context.close()
            result_json(False, "edit", error=str(e))


# ── REVIEW (convenience wrapper for edit --review) ─────────────────────────────
async def cmd_review(args):
    """Write or update review for a book (uses edit page)."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        context = await create_browser_context(p, headless=True)
        page = context.pages[0] if context.pages else await context.new_page()

        try:
            await _navigate_to_edit_page(page, args.book_id)

            textarea = await page.query_selector('textarea[name="review[review]"]')
            if not textarea:
                textarea = await page.query_selector('#review_review_usertext')

            if textarea:
                await textarea.fill("")
                await textarea.fill(args.text)
                await page.wait_for_timeout(500)

                save_btn = await page.query_selector(f'input#review_submit_for_{args.book_id}')
                if not save_btn:
                    save_btn = await page.query_selector('input[type="submit"][value="Save"]')
                if save_btn:
                    await save_btn.click()
                    await page.wait_for_timeout(3000)

                await context.close()
                result_json(True, "review", book_id=args.book_id,
                            review_preview=args.text[:100],
                            message=f"Đã cập nhật review")
            else:
                await context.close()
                result_json(False, "review", error="Không tìm thấy textarea review. Sách đã được shelve chưa?")

        except Exception as e:
            await context.close()
            result_json(False, "review", error=str(e))


# ── START READING ──────────────────────────────────────────────────────────────
async def cmd_start(args):
    """Mark book as 'Currently Reading' (start reading)."""
    # Reuse shelf command with currently-reading
    args.shelf_name = "currently-reading"
    await cmd_shelf(args)


# ── FINISH READING ─────────────────────────────────────────────────────────────
async def cmd_finish(args):
    """Mark book as 'Read' (finish reading)."""
    args.shelf_name = "read"
    await cmd_shelf(args)


# ── UPDATE PROGRESS ────────────────────────────────────────────────────────────
async def cmd_progress(args):
    """Update reading progress (page number or percentage)."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        context = await create_browser_context(p, headless=True)
        page = context.pages[0] if context.pages else await context.new_page()

        if not await check_logged_in(page):
            await context.close()
            result_json(False, "progress", error="Not logged in. Run: goodreads-writer.py login")

        await navigate_to_book(page, args.book_id)
        title = await page.text_content('h1[data-testid="bookTitle"], h1.Text__title1') or args.book_id

        try:
            # Look for "Update progress" button (only visible for currently-reading books)
            progress_btn = page.get_by_text("Update progress", exact=False)
            try:
                await progress_btn.click(timeout=5000)
            except Exception:
                # Book might not be on currently-reading shelf yet
                await context.close()
                result_json(False, "progress",
                            error="Nút 'Update progress' không tìm thấy. "
                                  "Sách cần ở shelf 'Currently Reading' trước. "
                                  "Chạy: goodreads-writer.py start <book_id>")

            await page.wait_for_timeout(1500)

            # Find the progress input field (page number or percentage)
            progress_input = await page.query_selector(
                'input[type="number"], input[placeholder*="page"], input[name*="progress"]'
            )
            if progress_input:
                await progress_input.fill("")
                await progress_input.fill(str(args.value))
                await page.wait_for_timeout(500)

                # Submit the progress
                submit_btn = page.get_by_role("button", name="Save").or_(
                    page.get_by_role("button", name="Submit")
                ).or_(
                    page.get_by_role("button", name="Update")
                )
                await submit_btn.first.click()
                await page.wait_for_timeout(2000)

                await context.close()
                result_json(True, "progress", book_id=args.book_id, title=title.strip(),
                            progress=args.value,
                            message=f"Đã cập nhật progress '{title.strip()}': {args.value}")
            else:
                await context.close()
                result_json(False, "progress", error="Không tìm thấy input progress.")

        except Exception as e:
            if "result_json" not in str(e):
                await context.close()
                result_json(False, "progress", error=str(e))


# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Goodreads Writer — Browser automation for OpenClaw agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s login                              # Đăng nhập (mở browser)
  %(prog)s status                             # Kiểm tra session
  %(prog)s rate 40121378 5                    # Rate Atomic Habits 5 sao
  %(prog)s shelf 40121378 read                # Chuyển sang shelf "Read"
  %(prog)s start 40121378                     # Bắt đầu đọc
  %(prog)s finish 40121378                    # Đọc xong
  %(prog)s review 40121378 "Great book!"      # Viết/cập nhật review
  %(prog)s edit 186190 --start-date 2025-01-15 --end-date 2025-02-20  # Sửa ngày đọc
  %(prog)s edit 186190 --stars 4 --review "Updated review"            # Sửa rating + review
  %(prog)s progress 40121378 150              # Cập nhật progress
        """
    )
    sub = parser.add_subparsers(dest="cmd")

    # login
    sub.add_parser("login", help="Mở browser để đăng nhập Goodreads (1 lần)")

    # status
    sub.add_parser("status", help="Kiểm tra trạng thái đăng nhập")

    # rate
    p_rate = sub.add_parser("rate", help="Chấm điểm sách (1-5 sao)")
    p_rate.add_argument("book_id", help="Goodreads book ID")
    p_rate.add_argument("stars", type=int, choices=[1, 2, 3, 4, 5], help="1-5 sao")

    # shelf
    p_shelf = sub.add_parser("shelf", help="Chuyển sách sang shelf")
    p_shelf.add_argument("book_id", help="Goodreads book ID")
    p_shelf.add_argument("shelf_name", help="read | currently-reading | to-read")

    # edit
    p_edit = sub.add_parser("edit", help="Sửa ngày đọc, review, rating (trang /review/edit/)")
    p_edit.add_argument("book_id", help="Goodreads book ID")
    p_edit.add_argument("--start-date", dest="start_date", help="Ngày bắt đầu đọc (YYYY-MM-DD)")
    p_edit.add_argument("--end-date", dest="end_date", help="Ngày đọc xong (YYYY-MM-DD)")
    p_edit.add_argument("--review", help="Nội dung review mới")
    p_edit.add_argument("--stars", type=int, choices=[1, 2, 3, 4, 5], help="Rating mới (1-5)")

    # review
    p_review = sub.add_parser("review", help="Viết/cập nhật review")
    p_review.add_argument("book_id", help="Goodreads book ID")
    p_review.add_argument("text", help="Nội dung review")

    # start
    p_start = sub.add_parser("start", help="Bắt đầu đọc (→ Currently Reading)")
    p_start.add_argument("book_id", help="Goodreads book ID")

    # finish
    p_finish = sub.add_parser("finish", help="Đọc xong (→ Read)")
    p_finish.add_argument("book_id", help="Goodreads book ID")

    # progress
    p_progress = sub.add_parser("progress", help="Cập nhật tiến độ đọc")
    p_progress.add_argument("book_id", help="Goodreads book ID")
    p_progress.add_argument("value", help="Số trang hoặc phần trăm")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    cmd_map = {
        "login": cmd_login,
        "status": cmd_status,
        "rate": cmd_rate,
        "shelf": cmd_shelf,
        "edit": cmd_edit,
        "review": cmd_review,
        "start": cmd_start,
        "finish": cmd_finish,
        "progress": cmd_progress,
    }

    asyncio.run(cmd_map[args.cmd](args))


if __name__ == "__main__":
    main()
