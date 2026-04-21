# Data Visualization

Animated charts, bar graphs, counters, comparisons, and infographics. Numbers come alive — bars race to their values, lines draw themselves, counters tick up from zero.

## The Goal

Data presented visually with animation that makes numbers intuitive. The viewer should understand the data point within 2 seconds of it appearing, and the animation should emphasize the key insight.

## When to Use

- **Statistics:** "73% of developers use AI tools" → animated bar or counter
- **Comparisons:** "React vs Vue vs Angular adoption" → racing bar chart
- **Trends:** "Growth over the last 5 years" → line chart drawing itself
- **Rankings:** "Top 5 frameworks by popularity" → horizontal bar chart
- **Proportions:** "Where the budget goes" → pie chart with slices appearing

## Approach 1: Remotion (Best — Animated)

**Requires:** `REMOTION_AVAILABLE = True` (set during Phase 0). If True, you MUST use Remotion for data viz — animated charts are dramatically more engaging than static images. See [remotion-setup.md](remotion-setup.md) for bootstrap and the BarChart/CounterReveal components.

### Bar Chart

```tsx
interface BarChartProps {
  bars: Array<{ label: string; value: number; color: string }>;
  title?: string;
  maxValue?: number;        // auto-calculated if omitted
  animationStyle: "grow" | "race" | "cascade";
  showValues: boolean;       // display number on/above each bar
  unit?: string;             // "%" or "M" or "$"
}
```

**Animation patterns:**
- `grow`: All bars grow simultaneously from 0 to their value
- `race`: Bars grow one at a time, left to right, with stagger
- `cascade`: Bars drop in from the top, one by one

### Line Chart

```tsx
interface LineChartProps {
  points: Array<{ x: string; y: number }>;
  lineColor: string;
  areaFill?: boolean;        // fill under the line
  drawDuration: number;      // frames to complete the line
  highlightPoint?: number;   // index of point to emphasize
}
```

### Counter

```tsx
interface CounterProps {
  targetValue: number;
  prefix?: string;           // "$" or ""
  suffix?: string;           // "%" or "M" or "users"
  duration: number;          // frames to count up
  fontSize: number;
  color: string;
}
```

### Rendering

```bash
npx remotion render src/Root.tsx BarChart \
  "{REMOTION_DIR}/output/chart_{segment_id}.mp4" \
  --props='{"bars":[{"label":"React","value":73,"color":"#61DAFB"}],...}' \
  --width=1280 --height=720
```

## Approach 2: AI Image (Acceptable — Static)

When Remotion is unavailable, generate a static chart image. Acceptable for simple bar charts and comparisons, but no animation.

```python
chart_img = coll.generate_image(
    prompt="Clean bar chart on dark background showing: React 73%, Vue 42%, Angular 31%, Svelte 18%. Blue bars, white labels, minimal professional style, data visualization",
    aspect_ratio="16:9",
)
```

**Prompt tips:**
- Include exact numbers in the prompt
- Specify "dark background" and "minimal professional style"
- Name the chart type (bar chart, pie chart, line chart)
- Keep to 4-6 data points for readability
- AI-generated charts may have inaccurate proportions — acceptable for mood, not for precision

## Approach 3: Playwright HTML (Good — Static but Precise)

For accurate charts, render with Chart.js in a local HTML file:

```python
def capture_chart(chart_config_json: str, work_dir: str = WORK_DIR) -> str:
    screenshot_dir = Path(work_dir) / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(screenshot_dir / f"chart_{uuid.uuid4().hex[:6]}.png")
    html_path = str(screenshot_dir / f"chart_{uuid.uuid4().hex[:6]}.html")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  body {{ margin:0; background:#0d1117; display:flex; align-items:center;
         justify-content:center; height:100vh; }}
  canvas {{ max-width:1100px; max-height:600px; }}
</style>
</head>
<body>
  <canvas id="chart"></canvas>
  <script>
    Chart.defaults.color = '#e6edf3';
    Chart.defaults.borderColor = '#30363d';
    new Chart(document.getElementById('chart'), {chart_config_json});
  </script>
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

## Style Guide

| Property | Value |
|----------|-------|
| Background | `#0d1117` |
| Grid lines | `#30363d` (subtle) |
| Text color | `#e6edf3` (light grey) |
| Font | System sans-serif, 14-18px for labels |
| Bar colors | Use the topic accent palette (see kinetic-text.md) |
| Max bars | 6-8 for readability |
| Value labels | Always show — the number is the point |

## Duration

| Chart type | Duration |
|-----------|----------|
| Single counter | 3-4s |
| Bar chart (3-5 bars) | 4-6s |
| Bar chart (6-8 bars) | 6-8s |
| Line chart | 5-7s |
| Pie chart | 4-6s |
| Comparison (2 items) | 3-5s |

## SFX Pairing

- **Tick/count sound** during counter animations
- **Pop** when each bar reaches its value
- **Rise/swell** as a line chart draws upward
- **Impact** on the key data point (the highest bar, the crossing point)

## Combining with Text Overlays

Pair data_viz with a TextAsset callout for the key takeaway:

```python
# Main chart visual
visual_track.add_clip(seg_start, Clip(
    asset=VideoAsset(id=chart_video.id, volume=0),
    duration=6,
))

# Key stat callout appears 2 seconds into the chart
callout_track.add_clip(seg_start + 2, Clip(
    asset=TextAsset(
        text="73% adoption",
        font=Font(family="Clear Sans", size=48, color="#61DAFB"),
        background=Background(color="#000000", opacity=0.7, width=400, height=80),
    ),
    duration=4,
    position=Position.top_left,
    offset=Offset(x=0.05, y=0.05),
))
```
