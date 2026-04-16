# bb_info

A small [Playwright](https://playwright.dev/python/) script that logs into **CUHKSZ Blackboard** (`bb.cuhk.edu.cn`), then exports a text summary of:

- **Course Announcements** (stream items on the Course Announcement page)
- **Current Courses** (My Courses widget)
- **Due items** — each unique task from the Notifications **What’s Due** list, with **title**, **course name**, and **due date/time** from the assignment detail page (deduplicated by Blackboard’s `actionSelected` id)

Output is written to `course_data_summary.txt` in the **current working directory** (typically this project folder).

---

## Requirements

- Python 3.10+ (recommended)
- Dependencies: see `requirements.txt` (core: `playwright`)

Install Python packages:

```bash
pip install -r requirements.txt
```

Install the browser used by Playwright (Chromium):

```bash
playwright install chromium
```

---

## Configuration

Create **`secrets.json`** next to `bb_info.py` (this file is listed in `.gitignore` — do not commit it):

```json
{
  "account": "your_student_id_or_username",
  "password": "your_password"
}
```

---

## Usage

From the directory that contains `bb_info.py` and `secrets.json`:

```bash
python bb_info.py
```

The script runs **headless** by default and prints progress lines (login, fetching announcements, courses, due deadlines, each due item). On success it writes **`course_data_summary.txt`** and prints total execution time.

To debug with a visible browser, edit `bb_info.py` and set `headless=False` in `chromium.launch(...)`.

---

## Output format

`course_data_summary.txt` contains labeled sections:

1. **Course Announcement** — announcement blocks as plain text
2. **Current Courses** — text from the My Courses area
3. **Due items** — one line per unique due item:
  `title | course_name | due_datetime_from_detail_page`

---

## Limitations

- UI selectors match **this Blackboard instance**; if your institution updates the portal, locators may need updates.
- Same task can appear in more than one time bucket in the UI; duplicates are collapsed using the `item_id` parsed from each link’s `onclick` handler.

---

## License

Use at your own risk for personal automation. Keep credentials private.