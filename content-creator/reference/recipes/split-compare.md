# Split & Compare

Side-by-side comparisons showing two things simultaneously — before/after, old vs new, language A vs language B, approach X vs approach Y.

## The Goal

A vertically divided frame with two panels showing contrasting content. The viewer instantly sees the difference. Works for code comparisons, performance metrics, UI before/after, and conceptual contrasts.

## When to Use

- **Before/after:** Old code vs new code (e.g., JSON.parse hack vs structuredClone)
- **Language comparison:** Python vs JavaScript syntax
- **Performance:** Slow approach (with metrics) vs fast approach
- **Feature comparison:** Library A vs Library B
- **Conceptual contrast:** "What people think" vs "Reality"

## Approach 1: Remotion (Best — Animated)

**Requires:** `REMOTION_AVAILABLE = True` (set during Phase 0). If True, you MUST use Remotion for split-screen — animated reveal is what makes comparisons impactful. See [remotion-setup.md](remotion-setup.md) for bootstrap and the SplitCompare component.

### Component structure

```tsx
interface SplitCompareProps {
  leftPanel: {
    label: string;           // "Before" or "Python" or "Slow"
    content: string;         // code, text, or image URL
    contentType: "code" | "text" | "image";
    language?: string;       // for code syntax highlighting
    accentColor: string;     // red for "bad", green for "good"
  };
  rightPanel: {
    label: string;
    content: string;
    contentType: "code" | "text" | "image";
    language?: string;
    accentColor: string;
  };
  revealStyle: "simultaneous" | "left-first" | "wipe";
  dividerColor?: string;
}
```

### Animation patterns

| Style | Effect | When to use |
|-------|--------|-------------|
| `simultaneous` | Both panels appear at once | Direct comparison |
| `left-first` | Left panel appears, pause, then right panel | "Old way... NEW way" narrative |
| `wipe` | Divider slides from left to right, revealing right panel | Before/after reveal |

### Rendering

```bash
npx remotion render src/Root.tsx SplitCompare \
  "{REMOTION_DIR}/output/split_{segment_id}.mp4" \
  --props='{"leftPanel":{...},"rightPanel":{...}}' \
  --width=1280 --height=720
```

## Approach 2: Playwright Dual HTML (Good — Static)

When Remotion is unavailable, render two code blocks side by side in a local HTML file:

```python
def capture_split_code(left_code: str, right_code: str, language: str,
                        left_label: str, right_label: str,
                        work_dir: str = WORK_DIR) -> str:
    import html as html_module
    screenshot_dir = Path(work_dir) / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(screenshot_dir / f"split_{uuid.uuid4().hex[:6]}.png")
    html_path = str(screenshot_dir / f"split_{uuid.uuid4().hex[:6]}.html")

    left_escaped = html_module.escape(left_code)
    right_escaped = html_module.escape(right_code)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/{language}.min.js"></script>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0d1117; display:flex; height:100vh; font-family:system-ui; }}
  .panel {{ flex:1; padding:20px; display:flex; flex-direction:column; }}
  .panel:first-child {{ border-right: 2px solid #30363d; }}
  .label {{ color:#8b949e; font-size:14px; text-transform:uppercase; letter-spacing:2px;
            margin-bottom:12px; padding:6px 12px; border-radius:6px; display:inline-block; }}
  .label.bad {{ background:#3d1f1f; color:#f85149; }}
  .label.good {{ background:#1f3d2a; color:#3fb950; }}
  pre {{ flex:1; border-radius:8px; overflow:hidden; }}
  code {{ font-family:'JetBrains Mono','Fira Code',monospace !important;
          font-size:14px !important; line-height:1.5 !important;
          padding:20px !important; }}
  .hljs {{ background:#161b22 !important; }}
</style>
</head>
<body>
  <div class="panel">
    <span class="label bad">{left_label}</span>
    <pre><code class="language-{language}">{left_escaped}</code></pre>
  </div>
  <div class="panel">
    <span class="label good">{right_label}</span>
    <pre><code class="language-{language}">{right_escaped}</code></pre>
  </div>
  <script>hljs.highlightAll();</script>
</body>
</html>"""

    Path(html_path).write_text(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={{"width": 1280, "height": 720}})
        page.goto(f"file://{{html_path}}")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        page.screenshot(path=output_path)
        browser.close()

    return output_path
```

## BANNED Approach

**Do NOT use `generate_image` for split screen.** AI generators produce unreliable layouts — panels misaligned, content duplicated between sides, wrong proportions.

## Layout Patterns

### Vertical split (most common)
```
┌─────────────┬─────────────┐
│  Before     │  After      │
│  (red)      │  (green)    │
│             │             │
│  code/text  │  code/text  │
│             │             │
└─────────────┴─────────────┘
```

### Horizontal split (for short comparisons)
```
┌───────────────────────────┐
│  Before (red)             │
│  code/text                │
├───────────────────────────┤
│  After (green)            │
│  code/text                │
└───────────────────────────┘
```

## Style Guide

| Element | Before/Bad | After/Good |
|---------|-----------|------------|
| Label color | Red (`#f85149`) | Green (`#3fb950`) |
| Label background | Dark red (`#3d1f1f`) | Dark green (`#1f3d2a`) |
| Border accent | Red | Green |
| Panel background | Same dark (`#161b22`) | Same dark |

Keep both panels on the same dark background — color differentiation comes from labels and accents only.

## Duration

| Reveal style | Duration |
|-------------|----------|
| Both panels at once | 4-6s |
| Left first, then right | 6-8s (3-4s each side) |
| Wipe reveal | 5-7s |

For the `left-first` style, the narration typically says "Here's the old way" (left appears), pause, "and here's the new way" (right appears).

## SFX Pairing

- **Pop** when each panel appears
- **Whoosh** on the wipe reveal transition
- **Rise/positive ding** when the "good" side appears
