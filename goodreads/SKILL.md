---
name: goodreads
description: >-
  Full Goodreads integration: read shelves, search books, get details/reviews via RSS,
  and write actions (rate, shelf, review, edit dates, progress) via Playwright browser automation.
  Use when user asks about reading list, books, ratings, or wants to update their Goodreads.
metadata:
  openclaw:
    category: "reading"
    requires:
      bins: ["python3"]
    notes:
      api: "Goodreads official API deprecated Dec 2020. Read uses RSS feeds + HTML scraping. Write uses Playwright browser automation with stealth mode."
---

# Goodreads Skill

Full read + write access to Goodreads via RSS feeds and Playwright browser automation.

## Scripts

```bash
# Read-only (RSS + scraping, no login required)
R=scripts/goodreads-rss.py

# Write (Playwright browser automation, requires one-time login)
W=scripts/goodreads-write.sh
```

## Setup

See `references/SETUP.md` for installation and first-time login instructions.

**Quick start:**
```bash
# Install dependencies
pip install playwright playwright-stealth
playwright install chromium

# Login to Goodreads (one-time, opens browser)
./scripts/goodreads-write.sh login
```

## User Configuration

Replace `<USER_ID>` with your Goodreads user ID in all commands below.

> **How to find your user ID:** Go to your Goodreads profile page. The URL will be like:
> `goodreads.com/user/show/12345678-yourname` — the number is your user ID.

For write commands with RSS verification, set:
```bash
export GOODREADS_USER_ID="<YOUR_USER_ID>"
```

---

## Read Commands

### 1. View shelf

```bash
python3 $R shelf <USER_ID> --shelf <shelf> [--limit N] [--sort <sort>]
```

| `--shelf` | Meaning |
|---|---|
| `currently-reading` | Currently reading |
| `read` | Already read |
| `to-read` | Want to read |
| `<custom>` | Custom shelf |

| `--sort` | Meaning |
|---|---|
| `date_read` | Date finished (default for `read`) |
| `date_added` | Date added to shelf |
| `rating` | Personal rating |
| `title` | Book title |
| `author` | Author name |
| `avg_rating` | Average Goodreads rating |

**Examples:**
```bash
python3 $R shelf <USER_ID> --shelf currently-reading
python3 $R shelf <USER_ID> --shelf read --limit 20 --sort date_read
python3 $R shelf <USER_ID> --shelf to-read --limit 50
python3 $R shelf <USER_ID> --shelf read --limit 200 --sort rating
```

**Fields returned:** title, author, book_id, isbn, user_rating (0–5), average_rating, date_read, date_added, review, shelves, description (300 chars), published, book_url

### 2. Recent activity

```bash
python3 $R activity <USER_ID> [--limit N]
```

Returns: books added, marked read, reviews written...

### 3. Search books

```bash
python3 $R search "<query>" [--limit N]
```

```bash
python3 $R search "Jared Diamond" --limit 10
python3 $R search "atomic habits" --limit 5
```

Returns: book_id, title, author, book_url

### 4. Book details

```bash
python3 $R book <book_id>
```

Returns: title, author, average_rating, rating_count, review_count, description, isbn, published, genres, image_url

### 5. Book reviews

```bash
python3 $R reviews <book_id> [--limit N]
```

> ⚠️ Reviews are rendered via React — available count may be limited.

---

## Write Commands

> Requires one-time login. Run `$W login` first. Session persists for weeks/months.

### 1. Check login status

```bash
$W status
```

### 2. Rate a book

```bash
$W rate <book_id> <stars>
```

Stars: 1–5 (integer)

```bash
$W rate 40121378 5        # Rate Atomic Habits 5 stars
```

### 3. Change shelf

```bash
$W shelf <book_id> <shelf_name>
```

| `shelf_name` | Display | Notes |
|---|---|---|
| `to-read` | Want to Read | |
| `currently-reading` | Currently Reading | |
| `read` | Read | |

Output includes `"verified": true/false` — RSS auto-confirms after action.

```bash
$W shelf 186190 read                # Move to "Read"
$W shelf 186190 currently-reading   # Move to "Currently Reading"
```

### 4. Start reading

```bash
$W start <book_id>
```

Shortcut for `shelf <book_id> currently-reading`. RSS verified.

### 5. Finish reading

```bash
$W finish <book_id>
```

Shortcut for `shelf <book_id> read`. RSS verified.

### 6. Edit (dates, review, rating)

```bash
$W edit <book_id> [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD] [--stars N] [--review "text"]
```

Uses the `/review/edit/` page — can edit everything in **one command**.

> ⚠️ Book must be shelved first (use `$W shelf` or `$W start`).

**Examples:**
```bash
$W edit 186190 --start-date 2025-01-15 --end-date 2025-02-20
$W edit 186190 --stars 4
$W edit 186190 --review "Great book, highly recommend."
$W edit 186190 --start-date 2025-03-01 --end-date 2025-03-08 --stars 4 --review "Updated review"
```

### 7. Write/Update review

```bash
$W review <book_id> "<text>"
```

### 8. Update reading progress

```bash
$W progress <book_id> <page_or_percent>
```

> ⚠️ Book must be on `currently-reading` shelf.

```bash
$W progress 13618551 150    # Reading page 150
```

---

## Sample Workflows

### "What am I currently reading?"
```bash
python3 $R shelf <USER_ID> --shelf currently-reading
```

### "Find books about Japanese history"
```bash
python3 $R search "Japanese history" --limit 10
# → get book_id → python3 $R book <id> for details
```

### "I just finished Forrest Gump, rate 4 stars, read from 3/1 to 3/8"
```bash
$W finish 186190
$W edit 186190 --stars 4 --start-date 2025-03-01 --end-date 2025-03-08
```

### "Start reading Atomic Habits"
```bash
$W start 40121378
```

---

## Output Format

All commands return JSON:
```json
{
  "success": true,
  "action": "edit",
  "book_id": "186190",
  "changes": ["start_date=2025-03-01", "end_date=2025-03-08", "stars=4"],
  "message": "Updated: start_date=2025-03-01, end_date=2025-03-08, stars=4"
}
```

## Limitations

| Feature | Status |
|---|---|
| Read shelf | ✅ RSS, max 200 books/request |
| Activity feed | ✅ RSS |
| Search books | ✅ Scraping |
| Book details | ✅ Scraping + JSON-LD |
| Reviews | ⚠️ Limited scraping |
| Rate (1-5 stars) | ✅ |
| Change shelf (+ RSS verify) | ✅ |
| Start/Finish reading | ✅ |
| Write/edit review | ✅ |
| Edit reading dates | ✅ |
| Update progress | ✅ (requires currently-reading) |
| Session persistence | ✅ (stealth, weeks/months) |
| Remove from shelf | ❌ Not supported |
| Custom shelves (write) | ❌ Only 3 main shelves |

> **Note**: Goodreads may change its UI → scripts may break. If errors occur, check selectors.
> **Anti-bot**: Uses `playwright-stealth` + `--disable-blink-features=AutomationControlled`.
