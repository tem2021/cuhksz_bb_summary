import time
import json
import re
from pathlib import Path
from playwright.sync_api import Page, Playwright, sync_playwright

def squeeze(s: str) -> str:
    return " ".join(s.split())


def expand_due_view_blocks(page: Page) -> None:
    page.locator("#block\\:\\:1-dueView\\:\\:1-dueView_1").click()
    page.locator("#block\\:\\:1-dueView\\:\\:1-dueView_2").click()
    page.locator("#block\\:\\:1-dueView\\:\\:1-dueView_3").click()
    page.locator("#block\\:\\:1-dueView\\:\\:1-dueView_4").click()


def run(playwright: Playwright) -> None:

    secrets = json.loads(Path("secrets.json").read_text())
    account = secrets["account"]
    password = secrets["password"]

    # browser = playwright.chromium.launch(headless=False)
    browser = playwright.chromium.launch(headless=True)

    context = browser.new_context(
        locale="en-HK", 
        timezone_id="Asia/Hong_Kong",
        viewport={"width": 1280, "height": 720},
    )

    page = context.new_page()
    print("Logging in...")
    page.goto("https://bb.cuhk.edu.cn/")
    page.get_by_role("button", name="LOGIN").click()
    page.get_by_role("textbox", name="User Account").click()
    page.get_by_role("textbox", name="User Account").fill(account)
    page.get_by_role("button", name="下一步 Next").click()
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="登 录 Login").click()
    page.get_by_role("button", name="OK").click()
    page.locator("#global-nav-link").click() 
    page.locator("#AlertsOnMyBb_____AlertsTool").click() 
    page.locator('iframe[name="mybbCanvas"]').content_frame.get_by_role("link", name="Course Announcement").click()

    print("Fetching course announcements...")
    items = page.frame_locator('iframe[name="mybbCanvas"]').locator('div.stream_item')
    items.first.wait_for(state="visible", timeout=20000)
    all_texts = items.all_inner_texts()

    with open("course_data_summary.txt", "w", encoding="utf-8") as f:

        # -- section: course announcement --- 
        f.write("=== SECTION: Course Announcement === \n\n")
        for i, text in enumerate(all_texts, 1):
            clean_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            f.write(f"--- annoucement #{i} ---\n{clean_text}\n\n" + "="*40 + "\n\n")
        f.write("=" * 80 + "\n\n")

        page.get_by_role("link", name="Home", exact=True).click()
        print("Fetching current courses...")
        my_courses = page.locator("#My_Courses_Tools")

        # -- section: current courses --
        f.write("=== SECTION: Current Courses === \n\n")
        f.write(my_courses.inner_text())
        f.write("\n\n" + "=" * 80 + "\n\n")

        # -- section: due items (title | course | due on detail page) ---
        print("Fetching due deadlines (DDL)...")
        page.get_by_role("link", name="Notifications Dashboard").click()
        expand_due_view_blocks(page)

        f.write("=== SECTION: Due items === \n\n")

        due_row_sel = "#dueView ul.itemGroups > li"
        title_sel = 'a[href="javascript:void(0)"][onclick*="actionSelected"]'

        due_by_id: dict[str, dict[str, str]] = {}
        order: list[str] = []
        n = page.locator(due_row_sel).count()
        for i in range(n):
            row = page.locator(due_row_sel).nth(i)
            onclick = row.locator(title_sel).get_attribute("onclick") or ""
            m = re.search(r"actionSelected\('([^']+)'", onclick)
            if not m:
                continue
            item_id = m.group(1)
            if item_id in due_by_id:
                continue
            due_by_id[item_id] = {
                "title": squeeze(row.locator(title_sel).inner_text()),
                "course": squeeze(row.locator("div.course > a").inner_text()),
            }
            order.append(item_id)

        total_due = len(order)
        for idx, item_id in enumerate(order):
            meta = due_by_id[item_id]
            print(f"Entering due item {idx + 1}/{total_due}: {meta['title']}")
            if idx > 0:
                page.go_back(wait_until="domcontentloaded")
                page.locator("#dueView").wait_for(state="visible", timeout=20000)
                expand_due_view_blocks(page)

            page.locator(
                f"xpath=//div[@id='dueView']//a[contains(@onclick, \"actionSelected('{item_id}'\")]"
            ).first.click()
            page.locator("#metadata").wait_for(state="visible", timeout=20000)
            due_text = squeeze(
                page.locator("#metadata .metaSection")
                .filter(has_text="Due Date")
                .locator(".metaField")
                .first.inner_text()
            )
            f.write(f"{meta['title']} | {meta['course']} | {due_text}\n")

        f.write("\n\n" + "=" * 80 + "\n\n")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    start_time = time.time() 
    run(playwright)
    print(
        f"Total Execution Time: {time.time() - start_time:.2f} seconds"
    )

