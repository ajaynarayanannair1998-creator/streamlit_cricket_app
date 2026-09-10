from playwright.sync_api import sync_playwright

APP_URL = "https://iplanalyticspersonal.streamlit.app"

def wake_app():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        print(f"Visiting {APP_URL} ...")
        page.goto(APP_URL, timeout=60000)

        page.wait_for_timeout(8000)

        try:
            wake_button = page.get_by_text("Yes, get this app back up!", exact=False)
            if wake_button.is_visible(timeout=3000):
                print("App was asleep. Clicking wake-up button...")
                wake_button.click()
                page.wait_for_timeout(15000)
        except Exception:
            pass

        print("Done. Page title:", page.title())
        browser.close()

if __name__ == "__main__":
    wake_app()
