# Browser Recording with Playwright

Playwright Python API patterns for capturing browser navigation as video or screenshots. The agent writes and executes these scripts directly — no external skills or CLIs needed.

**All paths must use the run's `WORK_DIR`** (see SKILL.md "Parallel Execution"). Never use bare `/tmp/` paths.

## Setup

Install before first use:

```bash
pip install playwright && playwright install chromium
```

Runtime availability check:

```python
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
```

If `PLAYWRIGHT_AVAILABLE` is False, fall back to kinetic text (see asset-production.md).

## Video Recording

Playwright records everything a browser context does into a `.webm` file.

```python
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

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
    time.sleep(2)

    for _ in range(5):
        page.evaluate("window.scrollBy(0, 300)")
        time.sleep(1)

    video_path = page.video.path()
    context.close()
    browser.close()

print(f"Recorded: {video_path}")
```

**Key rules:**
- Call `page.video.path()` **before** `context.close()`
- Call `context.close()` to **flush** the video
- `record_video_size` should match `viewport`
- Use 1280x720 for landscape, 720x1280 for vertical
- Videos are `.webm` format — upload directly to VideoDB

## Screenshots

### Full-page screenshot

```python
screenshot_dir = Path(WORK_DIR) / "screenshots"
screenshot_dir.mkdir(parents=True, exist_ok=True)

page.goto("https://example.com/article")
page.wait_for_load_state("networkidle")
page.screenshot(path=str(screenshot_dir / "article_full.png"), full_page=True)
```

### Viewport screenshot

```python
page.screenshot(path=str(screenshot_dir / "article_viewport.png"))
```

### Element screenshot

```python
element = page.locator("article[data-testid='tweet']")
element.wait_for(state="visible", timeout=10000)
element.screenshot(path=str(screenshot_dir / "tweet.png"))
```

## Navigation Patterns

### Slow deliberate scroll (for recording)

```python
scroll_distance = 300
pause = 1.0
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

```python
page.evaluate("document.body.style.zoom = '1.25'")
```

### Type into a search box

```python
page.goto("https://www.google.com")
page.wait_for_selector("textarea[name='q']", state="visible")
page.locator("textarea[name='q']").type("AI trends 2026", delay=80)
time.sleep(0.5)
page.keyboard.press("Enter")
page.wait_for_load_state("networkidle")
```

## Zoom and Crop Patterns (Explainer Format)

For explainer-style videos, browser captures should feel focused and punchy. Use these techniques:

### Zoomed viewport for code/docs

Capture at a higher zoom level so code or documentation fills the frame:

```python
context = browser.new_context(
    viewport={"width": 1280, "height": 720},
    record_video_dir=str(capture_dir),
    record_video_size={"width": 1280, "height": 720},
    device_scale_factor=1.5,  # renders at higher DPI
)
page = context.new_page()
page.goto("https://github.com/user/repo")
page.wait_for_load_state("networkidle")

# Zoom into the content area
page.evaluate("document.body.style.zoom = '1.4'")
time.sleep(1)
```

### Focus on specific element (crop effect)

Navigate to a page then scroll/zoom so only the relevant element fills the viewport:

```python
# Scroll to specific element
element = page.locator(".readme-content h2:has-text('Installation')")
element.scroll_into_view_if_needed()
time.sleep(0.5)

# Zoom in so it fills the viewport
page.evaluate("document.body.style.zoom = '1.5'")
time.sleep(2)  # hold for viewer
```

### GitHub repo showcase (3-5 second clip)

```python
def record_github_repo(repo_url: str, work_dir: str = WORK_DIR) -> str:
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
        page.goto(repo_url)
        page.wait_for_load_state("networkidle")

        # Zoom into repo header area
        page.evaluate("document.body.style.zoom = '1.3'")
        time.sleep(2)

        # Scroll to show stars/description
        page.evaluate("window.scrollBy(0, 200)")
        time.sleep(2)

        video_path = page.video.path()
        context.close()
        browser.close()

    return str(video_path)
```

### Code file display (for code_editor fallback)

When Remotion is unavailable, render code locally using a self-contained HTML file with highlight.js. **Do NOT use ray.so or carbon.sh URL fragment encoding** — multi-line code with special characters gets corrupted by `urllib.parse.quote()` and produces garbled screenshots.

```python
def capture_code_display(code: str, language: str, work_dir: str = WORK_DIR) -> str:
    """Render code as a styled HTML page and screenshot it with Playwright."""
    import html as html_module
    screenshot_dir = Path(work_dir) / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(screenshot_dir / f"code_{uuid.uuid4().hex[:6]}.png")
    html_path = str(screenshot_dir / f"code_{uuid.uuid4().hex[:6]}.html")

    escaped_code = html_module.escape(code)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/{language}.min.js"></script>
<style>
  body {{
    margin: 0; padding: 40px 50px;
    background: #0d1117;
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; box-sizing: border-box;
  }}
  pre {{
    margin: 0; width: 100%;
    border-radius: 12px; overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  }}
  code {{
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace !important;
    font-size: 18px !important;
    line-height: 1.6 !important;
    padding: 30px 35px !important;
  }}
  .hljs {{ background: #161b22 !important; }}
</style>
</head>
<body>
  <pre><code class="language-{language}">{escaped_code}</code></pre>
  <script>hljs.highlightAll();</script>
</body>
</html>"""

    Path(html_path).write_text(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(f"file://{html_path}")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        page.screenshot(path=output_path)
        browser.close()

    return output_path
```

**Why this works:** The code is written directly to a local HTML file as escaped HTML text — no URL encoding, no fragment parsing, no third-party service dependency. highlight.js provides real syntax highlighting via CDN. The screenshot is pixel-perfect every time.

## Recipes

### Record a tweet

```python
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

        try:
            page.wait_for_selector("article", state="visible", timeout=10000)
        except Exception:
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)

        time.sleep(4)

        video_path = page.video.path()
        context.close()
        browser.close()

    return str(video_path)
```

### Record a search journey

```python
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

        page.goto("https://www.google.com")
        page.wait_for_selector("textarea[name='q']", state="visible")
        page.locator("textarea[name='q']").type(query, delay=80)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        for _ in range(3):
            page.evaluate("window.scrollBy(0, 400)")
            time.sleep(1.5)

        try:
            first_result = page.locator("h3").first
            first_result.click()
            page.wait_for_load_state("networkidle")
            time.sleep(3)
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
        page.screenshot(path=output_path)
        browser.close()

    return output_path
```

### Multi-page recording

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
            time.sleep(2)
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 300)")
                time.sleep(0.8)

        video_path = page.video.path()
        context.close()
        browser.close()

    return str(video_path)
```

## Headless vs Headed

**Default: headless.** Chromium's modern headless mode supports video recording natively.

```python
browser = p.chromium.launch(headless=True)
```

If video recording produces blank frames in headless Linux, use `xvfb-run`:

```bash
xvfb-run python capture_script.py
```

On macOS, headless video recording works out of the box.

## Output Files

- **Video**: `.webm` files in `record_video_dir`. Upload directly to VideoDB.
- **Screenshots**: `.png` files at specified path.

Cleanup handled at run level — `shutil.rmtree(WORK_DIR)` in Phase 6.

## Error Handling

```python
def safe_capture(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        print(f"Browser capture failed: {e}")
        return None  # caller falls back to kinetic text
```

## Explainer Format Tips

- **Keep captures short**: 4-6 seconds max for explainer (vs 10-15 for briefing)
- **Zoom aggressively**: Use 1.3-1.5x zoom so content fills the frame at 720p
- **Focus on one thing**: Don't show an entire page — zoom into the specific headline, code block, or metric
- **Speed up navigation**: Reduce `time.sleep()` pauses to 0.5-1s between actions
- **Skip the journey**: For explainer, go directly to the target content — no typing-in-search-box preamble unless that's the point of the segment
