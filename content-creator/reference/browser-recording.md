# Browser Recording with Playwright

Playwright Python API patterns for capturing browser navigation as video or screenshots. The agent writes and executes these scripts directly — no external skills or CLIs needed.

**All paths must use the run's `WORK_DIR`** (see SKILL.md "Parallel Execution"). Never use bare `/tmp/` paths — multiple runs would collide.

## Setup

Install before first use:

```bash
pip install playwright && playwright install chromium
```

Runtime availability check — use at the top of any script:

```python
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
```

If `PLAYWRIGHT_AVAILABLE` is False, fall back to kinetic text (see asset-production.md).

## Video Recording

Playwright records everything a browser context does into a `.webm` file. Enable it by passing `record_video_dir` when creating a context.

```python
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# WORK_DIR comes from the run's slug — e.g. "/tmp/vb_a1b2c3d4"
capture_dir = Path(WORK_DIR) / "captures"
capture_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        record_video_dir=str(capture_dir),
        record_video_size={"width": 1280, "height": 720},
    )
    page = context.new_page()

    page.goto("https://example.com")
    page.wait_for_load_state("networkidle")
    time.sleep(2)  # hold on content for viewer to read

    # scroll slowly through the page
    for _ in range(5):
        page.evaluate("window.scrollBy(0, 300)")
        time.sleep(1)

    # CRITICAL: get video path BEFORE closing context
    video_path = page.video.path()

    # CRITICAL: close context to flush the video file to disk
    context.close()
    browser.close()

# video_path is now a .webm file ready for upload to VideoDB
print(f"Recorded: {video_path}")
```

**Key rules:**
- Call `page.video.path()` **before** `context.close()` — the path object becomes invalid after close
- Call `context.close()` to **flush** the video — without this the file is incomplete/empty
- `record_video_size` should match `viewport` for crisp output
- Use 1280x720 for landscape, 720x1280 for vertical
- Videos are `.webm` format (VP8 codec) — upload directly to VideoDB

## Screenshots

### Full-page screenshot

Captures the entire scrollable page as a single tall image:

```python
screenshot_dir = Path(WORK_DIR) / "screenshots"
screenshot_dir.mkdir(parents=True, exist_ok=True)

page.goto("https://example.com/article")
page.wait_for_load_state("networkidle")
page.screenshot(path=str(screenshot_dir / "article_full.png"), full_page=True)
```

### Viewport screenshot

Captures only what's visible in the current viewport:

```python
page.screenshot(path=str(screenshot_dir / "article_viewport.png"))
```

### Element screenshot

Captures a specific element (a tweet embed, a chart, a headline):

```python
element = page.locator("article[data-testid='tweet']")
element.wait_for(state="visible", timeout=10000)
element.screenshot(path=str(screenshot_dir / "tweet.png"))
```

## Navigation Patterns

### Slow deliberate scroll (for recording)

The viewer needs time to read. Scroll in small increments with pauses:

```python
scroll_distance = 300  # pixels per step
pause = 1.0            # seconds between steps
steps = 6

for _ in range(steps):
    page.evaluate(f"window.scrollBy(0, {scroll_distance})")
    time.sleep(pause)
```

### Wait for dynamic content

```python
page.wait_for_load_state("networkidle")
page.wait_for_selector("article", state="visible", timeout=15000)
```

### Dismiss cookie banners and popups

Try common selectors — fail silently if not found:

```python
dismiss_selectors = [
    "button:has-text('Accept')",
    "button:has-text('Got it')",
    "button:has-text('Close')",
    "[aria-label='Close']",
    ".cookie-banner button",
]
for sel in dismiss_selectors:
    try:
        btn = page.locator(sel).first
        if btn.is_visible(timeout=2000):
            btn.click()
            time.sleep(0.5)
            break
    except Exception:
        continue
```

### Zoom for readability

Scale the page up so text is legible at 720p:

```python
page.evaluate("document.body.style.zoom = '1.25'")
```

### Type into a search box (for search journey recordings)

```python
page.goto("https://www.google.com")
page.wait_for_selector("textarea[name='q']", state="visible")
# type slowly so the recording captures it
page.locator("textarea[name='q']").type("AI trends 2026", delay=80)
time.sleep(0.5)
page.keyboard.press("Enter")
page.wait_for_load_state("networkidle")
```

## Recipes

### Record a tweet

```python
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def record_tweet(tweet_url: str, work_dir: str = WORK_DIR) -> str:
    video_dir = Path(work_dir) / "captures"
    video_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(video_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()

        page.goto(tweet_url)
        page.wait_for_load_state("networkidle")

        # wait for tweet content to render
        try:
            page.wait_for_selector("article", state="visible", timeout=10000)
        except Exception:
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)

        # hold on the tweet for 4 seconds
        time.sleep(4)

        video_path = page.video.path()
        context.close()
        browser.close()

    return str(video_path)
```

For a static screenshot instead, replace the recording setup with a simple `page.screenshot()`:

```python
def screenshot_tweet(tweet_url: str, work_dir: str = WORK_DIR) -> str:
    screenshot_dir = Path(work_dir) / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(screenshot_dir / f"tweet_{uuid.uuid4().hex[:6]}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})

        page.goto(tweet_url)
        page.wait_for_load_state("networkidle")

        try:
            tweet = page.locator("article").first
            tweet.wait_for(state="visible", timeout=10000)
            tweet.screenshot(path=output_path)
        except Exception:
            time.sleep(3)
            page.screenshot(path=output_path)

        browser.close()

    return output_path
```

### Record a search journey

~10-15 seconds of footage showing the agent "researching live":

```python
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def record_search_journey(query: str, work_dir: str = WORK_DIR) -> str:
    video_dir = Path(work_dir) / "captures"
    video_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(video_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()

        # search
        page.goto("https://www.google.com")
        page.wait_for_selector("textarea[name='q']", state="visible")
        page.locator("textarea[name='q']").type(query, delay=80)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # scroll through results
        for _ in range(3):
            page.evaluate("window.scrollBy(0, 400)")
            time.sleep(1.5)

        # click first organic result
        try:
            first_result = page.locator("h3").first
            first_result.click()
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # hold on the article
        except Exception:
            time.sleep(2)

        video_path = page.video.path()
        context.close()
        browser.close()

    return str(video_path)
```

### Screenshot a news headline

```python
def screenshot_headline(article_url: str, work_dir: str = WORK_DIR) -> str:
    screenshot_dir = Path(work_dir) / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(screenshot_dir / f"headline_{uuid.uuid4().hex[:6]}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})

        page.goto(article_url)
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # viewport-only — captures the hero/headline area
        page.screenshot(path=output_path)
        browser.close()

    return output_path
```

### Multi-page recording (visit several URLs in one clip)

```python
def record_multi_page(urls: list[str], work_dir: str = WORK_DIR) -> str:
    video_dir = Path(work_dir) / "captures"
    video_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(video_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()

        for url in urls:
            page.goto(url)
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # hold on each page
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 300)")
                time.sleep(0.8)

        video_path = page.video.path()
        context.close()
        browser.close()

    return str(video_path)
```

## Headless vs Headed

**Default: headless.** The agent runs without a display. Chromium's modern headless mode (`--headless=new`, default in Playwright) supports video recording natively.

```python
browser = p.chromium.launch(headless=True)  # default, works for video
```

If video recording produces blank frames in a headless Linux environment (rare), use `xvfb-run`:

```bash
xvfb-run python capture_script.py
```

On macOS (typical dev machine), headless video recording works out of the box.

## Output Files

- **Video**: Playwright writes `.webm` files to `record_video_dir` (auto-generated UUID filenames). Upload directly to VideoDB.
- **Screenshots**: `.png` files at the exact `path` you specified.

After uploading all captures to VideoDB, clean up is handled at the run level — `shutil.rmtree(WORK_DIR)` in Phase 6 (see SKILL.md).

## Error Handling

Wrap Playwright operations so a single failed capture doesn't crash the whole pipeline:

```python
def safe_capture(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        print(f"Browser capture failed: {e}")
        return None  # caller falls back to kinetic text
```
