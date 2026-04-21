# Code Slide

Show code with syntax highlighting, readable at 720p. This is the **primary visual type for explainer format** — every topic involving code should use this.

## The Goal

A dark-themed code editor frame showing real, accurate code with proper syntax highlighting. Optionally animated with typing, line-by-line reveals, zoom effects, and cursor blinks. Think VS Code screenshot but cinematic.

## Approach 1: Remotion (Best — Animated)

**Requires:** `REMOTION_AVAILABLE = True` (set during Phase 0 bootstrap). **If Phase 0 set this to True, you MUST use Remotion for code slides, not Playwright.** Playwright is a fallback only.

Write a `CodeEditor.tsx` component into the scaffolded Remotion project:

```tsx
interface CodeEditorProps {
  code: string;
  language: string;
  highlightLines?: number[];
  typingSpeed?: number;       // characters per frame
  theme?: "dark" | "monokai" | "dracula";
  fileName?: string;          // shown in tab bar
  zoomToLine?: number;        // zoom into this line mid-animation
}
```

### Animation patterns

| Pattern | When to use | Duration |
|---------|-------------|----------|
| Typing reveal | Short snippets (< 8 lines) | 3-6s |
| Line-by-line appear | Medium snippets (8-15 lines) | 4-8s |
| Instant + highlight | Comparison (old vs new) | 3-5s |
| Zoom to function | Long file with key area | 5-8s |

### Rendering

```bash
# Animated video (typing effect)
npx remotion render src/Root.tsx CodeEditor \
  "{REMOTION_DIR}/output/code_{segment_id}.mp4" \
  --props='{"code":"...","language":"javascript","typingSpeed":3}' \
  --width=1280 --height=720

# Static still (faster, no animation)
npx remotion still src/Root.tsx CodeEditor \
  "{REMOTION_DIR}/output/code_{segment_id}.png" \
  --props='{"code":"...","language":"javascript"}' \
  --frame=60
```

Upload the output to VideoDB as `VideoAsset` (animated) or `ImageAsset` (still).

## Approach 2: Playwright Local HTML (Fallback — Static)

**Use ONLY when `REMOTION_AVAILABLE = False`.** Renders code as a self-contained HTML page with highlight.js and screenshots it. Produces a static image (no animation), but guarantees accurate, syntax-highlighted code.

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

Upload the PNG to VideoDB as an `ImageAsset`.

### Customizing the theme

Swap the highlight.js stylesheet URL to change theme:

| Theme | CDN path |
|-------|----------|
| GitHub Dark (default) | `styles/github-dark.min.css` |
| Monokai | `styles/monokai.min.css` |
| Dracula | `styles/dracula.min.css` |
| One Dark | `styles/atom-one-dark.min.css` |
| Nord | `styles/nord.min.css` |

### Adding a window chrome (macOS dots)

For a more polished look, add a title bar to the HTML:

```html
<div style="background:#161b22; border-radius:12px 12px 0 0; padding:10px 16px; display:flex; gap:8px; align-items:center;">
  <div style="width:12px;height:12px;border-radius:50%;background:#ff5f57;"></div>
  <div style="width:12px;height:12px;border-radius:50%;background:#febc2e;"></div>
  <div style="width:12px;height:12px;border-radius:50%;background:#28c840;"></div>
  <span style="color:#8b949e;font-size:13px;margin-left:12px;font-family:system-ui;">{fileName}</span>
</div>
```

Insert this `div` before the `<pre>` tag and remove the `border-radius` from `pre`.

## BANNED Approaches

| Method | Why it fails |
|--------|-------------|
| `generate_image` | AI halluccinates code — garbled syntax, made-up variable names, unreadable text |
| `generate_video` | Same problem as images, but animated garbage |
| ray.so / carbon.sh via URL encoding | `urllib.parse.quote()` corrupts multi-line code with special characters in URL fragments — produces mojibake |

## Style Guide

| Property | Value |
|----------|-------|
| Background | `#0d1117` or `#1e1e1e` |
| Font family | JetBrains Mono, Fira Code, Cascadia Code, Consolas |
| Font size | 18-24px (must be readable at 720p) |
| Line height | 1.6 |
| Max visible lines | 15-20 (scroll/zoom for longer) |
| Syntax highlighting | Always on — never show plain white text |
| Comments | Muted grey (`#8b949e`) |
| Strings | Soft green or orange |
| Keywords | Purple or blue |

## Segment Duration

| Scenario | Duration |
|----------|----------|
| Short snippet (3-5 lines) | 3-5s |
| Medium snippet (6-12 lines) | 5-8s |
| Long snippet with explanation | 8-10s (split if longer) |
| Before/after comparison | Show "before" 3-4s, hard_cut to "after" 3-4s |

If narration for a code segment exceeds 10s, split into two visual segments: show the first half of the code, then cut to a zoomed/highlighted view of the key lines.

## SFX Pairing

- **Pop/click** when the code first appears (0.2s)
- **Typing sounds** if using Remotion typing animation (subtle, low volume)
- **Whoosh** if zooming into a specific function

## Combining with Overlays

Code slides benefit from overlays because they're static images held for several seconds:

- **Logo badge** in top-right corner showing the language/framework logo
- **PiP reaction meme** at second 3-4 of a long code segment
- **Ambient loop** (subtle particles) at `opacity=0.15` underneath for static screenshots

See [overlay-techniques.md](overlay-techniques.md) for placement rules.
