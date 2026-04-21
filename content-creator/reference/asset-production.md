# Asset Production

For each segment in the script, create a visual asset using the best approach for its `visual_type`. You are the host — you're producing footage for your show, not generating pretty pictures.

## Universal Sourcing Hierarchy

**Before producing ANY visual, follow this order:**

```
1. Search asset library collection (recipes/sourcing/asset-library.md)
      ↓ not found (score < 0.5)
2. Source from external API (appropriate sourcing recipe below)
      ↓ API unavailable or no results
3. Generate with AI (generate_image, generate_video, TextAsset)
      ↓ after sourcing/generating
4. Upload to asset library for future reuse
```

## Sourcing Recipe Router

Determines which sourcing recipe to read for each visual type:

| Visual Type | Sourcing Recipe | Then Visual Recipe |
|---|---|---|
| `stock_footage` | [stock-footage.md](recipes/sourcing/stock-footage.md) | (asset IS the visual) |
| `motion_scene` | [stock-footage.md](recipes/sourcing/stock-footage.md) (video) | Fallback: `generate_video` |
| `image_scene` | [stock-footage.md](recipes/sourcing/stock-footage.md) (photo) | Fallback: `generate_image` |
| `meme_insert` | [meme-sourcing.md](recipes/sourcing/meme-sourcing.md) | [meme-humor.md](recipes/meme-humor.md) |
| `logo_composition` | [logo-sourcing.md](recipes/sourcing/logo-sourcing.md) | (compose on timeline with scale/position) |
| `code_editor` | (none — always rendered) | [code-slide.md](recipes/code-slide.md) |
| `diagram_animation` | (none — always rendered) | [diagram-flow.md](recipes/diagram-flow.md) |
| `browser_capture` | (none — always live) | [browser-recording.md](../browser-recording.md) |
| `kinetic_text` | (none — TextAsset) | [kinetic-text.md](recipes/kinetic-text.md) |
| `split_screen` | (none — always rendered) | [split-compare.md](recipes/split-compare.md) |
| `data_viz` | (none — always rendered) | [data-viz.md](recipes/data-viz.md) |

**For overlays**, read:
- [gif-reactions.md](recipes/sourcing/gif-reactions.md) — PiP reactions and animated clips
- [logo-sourcing.md](recipes/sourcing/logo-sourcing.md) — logo badges in corners
- [stock-footage.md](recipes/sourcing/stock-footage.md) — ambient loop backgrounds

## Visual Type → Recipe Files

Each visual type has a dedicated recipe file with detailed production instructions, style guides, code examples, and fallback chains. **Read the recipe before producing each visual type.** For Remotion-rendered visual types, also read [remotion-setup.md](recipes/remotion-setup.md) for component definitions and rendering commands.

| Visual Type | Recipe File | Primary Method |
|---|---|---|
| `code_editor` | [code-slide.md](recipes/code-slide.md) | Remotion → Playwright HTML |
| `meme_insert` | [meme-humor.md](recipes/meme-humor.md) | Real memes (Imgflip/GIPHY) → `generate_image` |
| `kinetic_text` | [kinetic-text.md](recipes/kinetic-text.md) | VideoDB TextAsset |
| `diagram_animation` | [diagram-flow.md](recipes/diagram-flow.md) | Remotion SVG → Mermaid.js |
| `data_viz` | [data-viz.md](recipes/data-viz.md) | Remotion → Chart.js |
| `split_screen` | [split-compare.md](recipes/split-compare.md) | Remotion → Playwright dual HTML |
| `overlay (PiP)` | [overlay-techniques.md](recipes/overlay-techniques.md) | Real GIFs (GIPHY) / real logos (Simple Icons) |
| `motion_scene` | (below) | Stock video (Pexels) → `generate_video` |
| `browser_capture` | [browser-recording.md](../browser-recording.md) | Playwright |
| `image_scene` | (below) | Stock photo (Pexels) → `generate_image` |
| `logo_composition` | (below) | Real logos (Simple Icons CDN) |
| `stock_footage` | (below) | Pexels/Pixabay API |

## Banned Production Approaches

These combinations produce broken results. The self-review will reject them.

| Visual Type | BANNED Method | Why |
|---|---|---|
| `code_editor` | `generate_image` | AI hallucinates code — garbled syntax, made-up variables |
| `code_editor` | `generate_video` | Same problem, animated garbage |
| `code_editor` | ray.so/carbon.sh via URL encoding | `urllib.parse.quote()` corrupts multi-line code |
| `diagram_animation` | `generate_image` (for animation) | No animation possible |
| `split_screen` | `generate_image` | Layout unreliable — panels misaligned |
| `kinetic_text` | `generate_image` | Use TextAsset — faster, pixel-perfect |
| `browser_capture` | `generate_image` | The whole point is showing REAL content |
| `logo_composition` | `generate_image` | Logos will be wrong. Use real logos from CDN |

## Simple Visual Types (No Dedicated Recipe)

### Motion Scene

Atmospheric b-roll, hooks, transitions.

**Primary:** Search Pexels for cinematic video clips (see [stock-footage.md](recipes/sourcing/stock-footage.md)).

**Fallback:** AI video generation:
```python
video_clip = coll.generate_video(
    prompt="Drone shot pushing forward over a city at night, neon lights reflecting, cinematic",
)
```

- Duration: 5-8 seconds. Always mute (`volume=0`).
- Good for: hooks, transitions between major sections, emotional beats.

### Image Scene

Abstract concepts, mood backgrounds, establishing shots.

**Primary:** Search Pexels for matching photos (see [stock-footage.md](recipes/sourcing/stock-footage.md)).

**Fallback:** AI image generation:
```python
bg_img = coll.generate_image(
    prompt="Abstract dark technology background with subtle blue gradient and digital particles, minimalist",
    aspect_ratio="16:9",
)
```

- Keep segments under 5 seconds (static images over 5s feel like a slideshow).
- Pair with ambient loop overlay for segments >4s.

### Logo Composition

Tech logo grids, framework comparisons, ecosystem overviews.

**Primary:** Source real logos from Simple Icons CDN (see [logo-sourcing.md](recipes/sourcing/logo-sourcing.md)). Compose multiple logos on a dark background using VideoDB timeline positioning.

**Fallback (Remotion):** Animate logos appearing with spring physics and stagger.

### Stock Footage

Real-world b-roll from stock APIs.

**Primary:** Pexels/Pixabay (see [stock-footage.md](recipes/sourcing/stock-footage.md)).

**Fallback:** `generate_video` with a similar prompt.

- Keep to 3-5 seconds, mute audio, prefer clips with camera movement.

## Design Standards for Text Overlays

Hard minimums for any text rendered on screen (all sizes at 1280x720):

| Text Role | Font Size | Frame Width Coverage |
|---|---|---|
| Hero stat / section header | 52-72px | 60%+ |
| Data callout (lower-third) | 36-48px | 40%+ |
| Title card | 48-60px | 60%+ |
| Subtitle / attribution | 24-32px | — |

Every text overlay MUST have a semi-opaque background bar (opacity 0.6-0.8).

**CRITICAL — No TextAsset on Remotion segments:** Remotion-rendered videos (CodeEditor, KineticText, DiagramFlow, BarChart, SplitCompare, CounterReveal) already contain text baked into their frames. Do NOT add any `TextAsset` overlay on top. This causes ugly double-text. Remotion segments are visually self-contained and provide their own text through animation.

**Known gotcha:** `TextAsset` at `Position.center` with `Background` may render invisibly. Use `Position.bottom` with `Offset(y=-0.3)` to simulate center placement.

## Production Order

1. **Narration audio first.** Generate voiceover for each segment. Always cast `float(voice.length)` — it may return a string. Truncate with `math.floor(length * 100) / 100`.
2. **Background music second.** Generate one track. Check `music.length` — loop if needed.
3. **SFX third (if format requires it).** Whooshes, pops, comedic stings.
4. **Visuals: source before generate.** Search asset library and external APIs in parallel where possible. Generate AI assets only for what can't be sourced.
5. **Overlay assets (explainer format — MANDATORY).** After all main visuals are produced, make a second pass and produce overlay assets. See below.

**Critical:** AI-generated videos are 5-8 seconds max. Never set clip duration beyond actual `.length`.

## Overlay Asset Production (Phase 3, Step 5)

**This step is MANDATORY for fireship-explainer format.** The self-review will FAIL any explainer video with fewer than 3 overlay clips. Produce overlay assets AFTER main visuals so you know which segments need them.

### Planning pass

Walk through the segment list and assign overlays:

```python
overlay_plan = []
for seg in script["segments"]:
    vtype = seg["visual_type"]
    # Skip segments where overlays are banned
    if vtype in ("kinetic_text", "meme_insert"):
        continue
    
    if vtype == "code_editor":
        # Code slides → logo badge for the language/framework
        lang = seg.get("language", "javascript")
        overlay_plan.append({
            "segment_id": seg["id"],
            "type": "logo_badge",
            "source": f"simpleicons_{lang}",
            "position": "top_right",
            "scale": 0.08,
        })
    elif vtype == "diagram_animation" and seg.get("mentions_tech"):
        # Diagrams mentioning a tech → logo badge
        overlay_plan.append({
            "segment_id": seg["id"],
            "type": "logo_badge",
            "source": f"simpleicons_{seg['mentions_tech']}",
            "position": "top_right",
            "scale": 0.08,
        })
    elif vtype in ("image_scene", "data_viz") and seg.get("duration", 5) > 4:
        # Static visuals >4s → PiP reaction or ambient loop
        overlay_plan.append({
            "segment_id": seg["id"],
            "type": "pip_reaction",
            "query": "developer surprised",
            "position": "bottom_right",
            "scale": 0.20,
        })

# HARD CHECK
if len(overlay_plan) < 3:
    # Force-add overlays to the longest code_editor segments
    code_segs = sorted(
        [s for s in script["segments"] if s["visual_type"] == "code_editor"],
        key=lambda s: s.get("duration", 5), reverse=True
    )
    for cs in code_segs:
        if len(overlay_plan) >= 3:
            break
        if not any(o["segment_id"] == cs["id"] for o in overlay_plan):
            overlay_plan.append({
                "segment_id": cs["id"],
                "type": "logo_badge",
                "source": "simpleicons_" + cs.get("language", "javascript"),
                "position": "top_right",
                "scale": 0.08,
            })

print(f"Overlay plan: {len(overlay_plan)} overlays")
assert len(overlay_plan) >= 3, f"FAIL: Only {len(overlay_plan)} overlays — need at least 3"
```

### Producing overlay assets

| Overlay type | How to produce | Upload to |
|---|---|---|
| `logo_badge` | Download SVG from `https://cdn.simpleicons.org/{name}` → convert to PNG with Playwright screenshot → upload | `asset_coll` |
| `pip_reaction` | GIPHY API search → download MP4. Fallback: `generate_image` with reaction prompt | `asset_coll` |
| `ambient_loop` | Search asset library for existing ambient clips. Fallback: `generate_video("subtle particles dark background")` | `asset_coll` |
| `stat_counter` | No asset needed — use `TextAsset` directly during composition | N/A |

```python
# Example: download logo as PNG via Playwright
def download_logo_png(icon_name: str, work_dir: str, size: int = 128) -> str:
    """Download a Simple Icons SVG and render to PNG."""
    from playwright.sync_api import sync_playwright
    svg_url = f"https://cdn.simpleicons.org/{icon_name}/white"
    html = f'''<html><body style="margin:0;background:#0d1117;display:flex;
    align-items:center;justify-content:center;width:{size}px;height:{size}px;">
    <img src="{svg_url}" width="{size-16}" height="{size-16}"></body></html>'''
    html_path = f"{work_dir}/screenshots/logo_{icon_name}.html"
    png_path = f"{work_dir}/screenshots/logo_{icon_name}.png"
    Path(html_path).write_text(html)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": size, "height": size})
        page.goto(f"file://{html_path}")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=png_path)
        browser.close()
    return png_path
```

Save the overlay plan to `{WORK_DIR}/scripts/overlay_plan.json` for use during composition.

## Mixing Approaches

### Briefing format (data-heavy topic):
```
hook: motion_scene → context: browser_capture → insight 1: data_viz →
insight 2: kinetic_text → takeaway: data_viz → close: kinetic_text
```

### Fireship explainer format:
```
hook: kinetic_text → topic1_intro: kinetic_text → topic1_code: code_editor →
topic1_meme: meme_insert → topic2_intro: kinetic_text → topic2_code: code_editor →
topic2_compare: split_screen → topic2_meme: meme_insert →
topic3_intro: kinetic_text → topic3_code: code_editor →
topic3_data: data_viz → takeaway: kinetic_text → cta: logo_composition
```

**Key principle:** Visual type should change every 2-3 segments. If you find 3 consecutive `code_editor` segments, break them up with a `meme_insert`, `diagram_animation`, or `kinetic_text`.
