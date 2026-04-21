# Diagram & Flow

Animated architecture diagrams, data flow charts, concept maps, and process flows. Boxes appear, arrows draw themselves, labels fade in — the diagram builds itself as the narration explains it.

## The Goal

A dark-themed diagram that constructs itself piece by piece, synchronized with narration. The viewer sees the system come together rather than staring at a completed diagram trying to parse it.

## When to Use

- **Architecture overviews:** "Here's how the system works" — microservices, data pipelines
- **Process flows:** "First X happens, then Y" — deployment pipelines, request lifecycle
- **Concept maps:** "These three concepts relate like this" — mental models
- **Decision trees:** "If X then Y, otherwise Z" — algorithm explanation
- **Comparison flows:** "Old way vs new way" — showing improvement

## Approach 1: Remotion SVG (Best — Animated)

**Requires:** `REMOTION_AVAILABLE = True` (set during Phase 0). If True, you MUST use Remotion for diagrams — animated build-up is what makes diagrams effective. See [remotion-setup.md](remotion-setup.md) for bootstrap and the DiagramFlow component.

Build animated SVG-based diagrams that construct themselves piece by piece.

### Component structure

**Do NOT pass raw pixel coordinates for node positions.** The component in [remotion-setup.md](remotion-setup.md) auto-spaces nodes evenly across the 1280x720 canvas. Just pass nodes in order with `id`, `label`, and `color` — the layout is computed automatically.

```tsx
interface DiagramFlowProps {
  nodes: Array<{
    id: string;
    label: string;
    color?: string;    // border + glow color, defaults to #3498DB
  }>;
  edges: Array<{
    from: string;
    to: string;
    label?: string;
  }>;
  title?: string;       // shown at top center
}
```

### Animation sequence

1. Background appears (dark gradient)
2. First node fades in with slight scale overshoot (spring physics)
3. Connection line draws from first node toward second node (SVG path animation)
4. Second node fades in
5. Label on the connection fades in
6. Repeat until diagram is complete
7. Optional: highlight the "key path" with a glow or color change

### Style guide

| Property | Value |
|----------|-------|
| Background | `#0d1117` or dark gradient |
| Node shape | Rounded rectangles (`rx=12`) |
| Node fill | Semi-transparent with border (`fill-opacity: 0.15`, `stroke-width: 2`) |
| Node colors | Limit to 3-4 from palette |
| Edge style | Smooth bezier curves, animated dash or draw-in |
| Labels | White text, 16-20px, appear after their element |
| Arrow heads | Small, filled, matching edge color |
| Spring physics | Slight overshoot on node appear (makes it feel alive) |

### Color palette

```
Primary:   #3498DB (blue)    — main flow
Secondary: #2ECC71 (green)   — success path
Warning:   #E74C3C (red)     — error/failure path
Neutral:   #95A5A6 (grey)    — background connections
Accent:    #F39C12 (orange)  — highlighted element
```

### Rendering

```bash
npx remotion render src/Root.tsx DiagramFlow \
  "{REMOTION_DIR}/output/diagram_{segment_id}.mp4" \
  --props='{"nodes":[...],"edges":[...]}' \
  --width=1280 --height=720
```

## Approach 2: AI Image (Acceptable — Static)

When Remotion is unavailable, generate a static diagram image. Rename the visual type to `image_scene` in your internal tracking (since there's no animation).

```python
diagram_img = coll.generate_image(
    prompt="Clean architecture diagram showing [describe the flow], dark background, rounded boxes with labels, arrows connecting them, professional technical diagram style, blue and green color scheme, minimal",
    aspect_ratio="16:9",
)
```

**Prompt tips for diagram images:**
- Always specify "dark background"
- Describe each box and connection explicitly
- Say "professional technical diagram" not "flowchart"
- Limit to 4-6 boxes for readability at 720p
- Specify colors and shapes

**Limitations:** No animation, no build-up effect, and AI may misplace labels or connections. Acceptable for simple diagrams (3-4 boxes), unreliable for complex ones.

## Approach 3: Playwright HTML (Good — Static but Accurate)

Render a diagram using Mermaid.js in a local HTML file:

```python
def capture_diagram(mermaid_code: str, work_dir: str = WORK_DIR) -> str:
    import html as html_module
    screenshot_dir = Path(work_dir) / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(screenshot_dir / f"diagram_{uuid.uuid4().hex[:6]}.png")
    html_path = str(screenshot_dir / f"diagram_{uuid.uuid4().hex[:6]}.html")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<style>
  body {{ margin:0; background:#0d1117; display:flex; align-items:center;
         justify-content:center; min-height:100vh; }}
</style>
</head>
<body>
  <pre class="mermaid">
{mermaid_code}
  </pre>
  <script>
    mermaid.initialize({{ theme: 'dark', startOnLoad: true }});
  </script>
</body>
</html>"""

    Path(html_path).write_text(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={{"width": 1280, "height": 720}})
        page.goto(f"file://{{html_path}}")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        page.screenshot(path=output_path)
        browser.close()

    return output_path
```

Mermaid syntax is straightforward:
```
graph LR
    A[Client] --> B[Load Balancer]
    B --> C[Server 1]
    B --> D[Server 2]
    C --> E[(Database)]
    D --> E
```

## Layout Patterns

### Linear flow (left to right)
```
[Step 1] → [Step 2] → [Step 3] → [Result]
```
Best for: processes, pipelines, request lifecycle.

### Hub and spoke
```
        [Service B]
            ↑
[Service A] ← [API Gateway] → [Service C]
            ↓
        [Service D]
```
Best for: microservices, API architecture.

### Before/After (top and bottom)
```
[Old Way] ──→ [Problem] ──→ [Pain]
[New Way] ──→ [Solution] ──→ [Win]
```
Best for: showing improvement, migration.

## Duration

| Complexity | Nodes | Duration |
|-----------|-------|----------|
| Simple | 3-4 | 4-6s |
| Medium | 5-7 | 6-8s |
| Complex | 8+ | 8-10s (split if longer) |

For animated Remotion diagrams, the build-up takes 60-80% of the duration, then the completed diagram holds for the remaining 20-40%.

## SFX Pairing

- **Pop/click** each time a node appears
- **Whoosh** when an arrow draws between nodes
- **Rise/swell** when the final "key path" highlights
