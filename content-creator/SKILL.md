---
name: content-creator
description: Turn any research topic into a polished video with narration, dynamic visuals, and background music. Supports pluggable formats (briefing, fireship-explainer, and more). Researches via parallel subagents, scripts a narrative arc, sources real-world assets (stock footage, memes, logos) from APIs and a persistent VideoDB collection cache, produces assets, composes on a timeline, and self-reviews in a loop.
---

# Content Creator

## Configuration

```
MAX_ITERATIONS: 5
DEFAULT_RESOLUTION: 1280x720
DEFAULT_FORMAT: landscape
ASSET_COLLECTION_NAME: content_creator_assets
```

## Format Selection

Each video format is defined in its own recipe file under `reference/formats/`. **Read the selected format file before Phase 2** — it defines persona, pacing, narrative arc, sourcing strategy, and quality criteria.

| User asks for... | Format file |
|---|---|
| "briefing", "summary", "quick take", "60 seconds on" | [formats/briefing.md](reference/formats/briefing.md) |
| "explainer", "breakdown", "deep dive", "Fireship-style", "tech video" | [formats/fireship-explainer.md](reference/formats/fireship-explainer.md) |

If ambiguous, default to `briefing` for short requests and `fireship-explainer` for anything that implies depth or multiple topics.

## Production Method Diversity (CRITICAL)

**No single production method may dominate.** AI image generation (`generate_image`) is the easiest tool to reach for, but using it for every segment produces a narrated slideshow.

### Hard Rules (all formats)

1. **No single production method may be used for more than 50% of segments.**
2. **At least 3 different production methods** per video (from: real-sourced assets, Remotion, Playwright, AI video, AI image, TextAsset).
3. **`code_editor` MUST NOT use `generate_image`.** AI hallucinates code. Use Remotion or Playwright (local HTML+highlight.js).
4. **`diagram_animation` MUST NOT use `generate_image`.** No animation. Use Remotion SVG.
5. **`split_screen` MUST NOT use `generate_image`.** Layout unreliable. Use Remotion.
6. **`kinetic_text` MUST use VideoDB `TextAsset`.** Don't generate an image of text.
7. **Code screenshots MUST use local HTML+highlight.js** (see browser-recording.md `capture_code_display`). Never ray.so/carbon.sh URL encoding.

### Recommended Production Method Per Visual Type

| Visual Type | Primary Method | Fallback | NEVER use |
|---|---|---|---|
| `code_editor` | Remotion | Playwright (local HTML+highlight.js) | `generate_image`, ray.so URL encoding |
| `diagram_animation` | Remotion SVG | `generate_image` (static only, rename to `image_scene`) | — |
| `logo_composition` | Real logos (Simple Icons CDN) | `generate_image` | — |
| `split_screen` | Remotion | Playwright (side-by-side screenshots) | `generate_image` |
| `data_viz` | Remotion | `generate_image` (static chart fallback) | — |
| `motion_scene` | Stock footage (Pexels) | `generate_video` | — |
| `browser_capture` | Playwright recording | Playwright screenshot | `generate_image` |
| `kinetic_text` | VideoDB TextAsset | Remotion text component | `generate_image` |
| `meme_insert` | Real meme template (Imgflip/GIPHY) | `generate_image` | — |
| `image_scene` | Stock photo (Pexels) | `generate_image` | — |
| `stock_footage` | Pexels/Pixabay API | `generate_video` | — |

The self-review phase will **automatically fail** any video where >50% of segments use a single production method.

## Asset Sourcing Hierarchy

Before producing any visual, follow this priority. See [recipes/sourcing/asset-library.md](reference/recipes/sourcing/asset-library.md) for details.

```
1. SEARCH the asset library collection (instant, free, pre-indexed)
      ↓ not found
2. SOURCE from external APIs (Pexels, Imgflip, GIPHY, Simple Icons, etc.)
      ↓ not available
3. GENERATE with AI (generate_image, generate_video, TextAsset)
      ↓ after sourcing/generating
4. UPLOAD to asset library for future reuse
```

Each sourcing channel has its own recipe:

| Sourcing Recipe | File | Used for |
|---|---|---|
| Asset Library | [sourcing/asset-library.md](reference/recipes/sourcing/asset-library.md) | Cache search (always first) |
| Stock Footage | [sourcing/stock-footage.md](reference/recipes/sourcing/stock-footage.md) | `stock_footage`, `motion_scene`, `image_scene` |
| Meme Sourcing | [sourcing/meme-sourcing.md](reference/recipes/sourcing/meme-sourcing.md) | `meme_insert` |
| Logo Sourcing | [sourcing/logo-sourcing.md](reference/recipes/sourcing/logo-sourcing.md) | `logo_composition`, logo overlays |
| GIF Reactions | [sourcing/gif-reactions.md](reference/recipes/sourcing/gif-reactions.md) | PiP overlays, reaction clips |

## Parallel Execution

This skill supports parallel runs. Every run **must** generate a unique slug and namespace all local temp files under it.

### Slug Generation

```python
import uuid

SLUG = uuid.uuid4().hex[:8]
WORK_DIR = f"/tmp/vb_{SLUG}"
```

### What the slug isolates

| Resource | Path pattern |
|---|---|
| Browser capture videos | `{WORK_DIR}/captures/` |
| Screenshots | `{WORK_DIR}/screenshots/` |
| Downloaded review frames | `{WORK_DIR}/frames/` |
| Any temp scripts | `{WORK_DIR}/scripts/` |
| Remotion projects | `{WORK_DIR}/remotion/` |

### Rules

1. **Never use bare `/tmp/` paths.** Always use `{WORK_DIR}/...`.
2. **Create `WORK_DIR` early.** Run `Path(WORK_DIR).mkdir(parents=True, exist_ok=True)` in Phase 0.
3. **Pass `WORK_DIR` to all functions.**
4. **Clean up on completion.** `shutil.rmtree(WORK_DIR, ignore_errors=True)`.
5. **Log the slug.** `print(f"Video run: {SLUG}")`.

## Dependencies

**Required:** [VideoDB](https://videodb.io) — handles all media generation (images, video, voice, music, sound effects), timeline composition, indexing, search, and streaming. Install: `pip install videodb python-dotenv`. Get a free API key at [console.videodb.io](https://console.videodb.io).

**Optional tools (use if available, fall back gracefully if not):**
- **Remotion** — code-rendered animations: charts, code editors, diagrams, logos, split-screen. Fallback: Playwright or AI generation.
- **Playwright** — browser recording and screenshots. Navigate to real websites, capture code displays. Install: `pip install playwright && playwright install chromium`. See [browser-recording.md](reference/browser-recording.md).

**Optional API keys (set in environment for richer sourcing):**
- `PEXELS_API_KEY` — stock footage and photos from Pexels
- `GIPHY_API_KEY` — reaction GIFs and animated memes from GIPHY
- `PIXABAY_API_KEY` — stock footage fallback from Pixabay
- `IMGFLIP_USERNAME` / `IMGFLIP_PASSWORD` — captioned meme generation via Imgflip

If any key is missing, that sourcing channel is skipped gracefully. The video will still work — just with fewer real-world assets.

## Visual Types

The skill supports 11 visual types. Pick based on what communicates best:

| Visual Type | Use For | Primary Source |
|---|---|---|
| `data_viz` | Animated charts, bar graphs, counters | Remotion |
| `motion_scene` | Atmospheric b-roll, hooks, transitions | Stock video (Pexels) / AI video |
| `browser_capture` | Citing sources, showing evidence | Playwright |
| `kinetic_text` | Key quotes, stat highlights, punchy declarations | VideoDB TextAsset |
| `image_scene` | Abstract concepts, mood backgrounds | Stock photo (Pexels) / AI image |
| `code_editor` | Code with syntax highlighting | Remotion / Playwright HTML |
| `meme_insert` | Humor beats, joke images/clips | Real memes (Imgflip/GIPHY) |
| `diagram_animation` | Architecture diagrams, data flows | Remotion SVG |
| `logo_composition` | Tech logo grids, comparisons | Real logos (Simple Icons) |
| `split_screen` | Side-by-side comparisons | Remotion |
| `stock_footage` | Real-world b-roll clips | Pexels/Pixabay API |

## Pipeline

```
0. Pre-flight       → verify tools, bootstrap asset collection, read format file
1. Research         → parallel subagents investigate the topic
2. Script           → structure findings into a video script (format-driven)
3. Asset Production → source/create visuals (search → source → generate)
4. Composition      → arrange on timeline, generate stream
4.5 Captions        → (optional, user-requested) index spoken words, add auto-synced animated captions
5. Self-Review      → index draft, critique, identify fixes
6. Iterate/Deliver  → fix and recompose, or deliver final URL
```

### Phase 0: Pre-flight Checks

1. Generate slug and create `WORK_DIR` (with subdirs: `captures`, `screenshots`, `frames`, `scripts`, `remotion`, `sourced`, `review_frames`).
2. Connect to VideoDB. Find or create the `content_creator_assets` collection (see [sourcing/asset-library.md](reference/recipes/sourcing/asset-library.md)).
3. Check and install Playwright if missing (`pip install playwright && playwright install chromium`).
4. **Set up Remotion (MANDATORY ATTEMPT).** Follow [recipes/remotion-setup.md](reference/recipes/remotion-setup.md) for full bootstrap instructions, component library, and test render. Set `REMOTION_AVAILABLE = True/False` based on result.
5. Check which API keys are available (`PEXELS_API_KEY`, `GIPHY_API_KEY`, `IMGFLIP_USERNAME`, `IMGFLIP_PASSWORD`, `PIXABAY_API_KEY`).
6. **Read the selected format file** (`reference/formats/{format}.md`).
7. Print capability summary including `REMOTION_AVAILABLE`, `PLAYWRIGHT_AVAILABLE`, and which API keys are set.

#### Remotion Bootstrap (Phase 0, Step 4)

Remotion enables animated code, diagrams, transitions, split-screens, data viz, and kinetic text — visual types that are static/broken without it. **You MUST attempt this setup.** Only skip if it fails after the retry.

Full setup instructions, component library (CodeEditor, KineticText, DiagramFlow, BarChart, SplitCompare, WhipTransition, CounterReveal), and rendering commands are in [recipes/remotion-setup.md](reference/recipes/remotion-setup.md).

Quick summary:
1. Check `node --version && npm --version`
2. Scaffold project: `npm init -y && npm install remotion @remotion/cli react react-dom`
3. Write Root.tsx and component files from the recipe
4. Test render: `npx remotion still src/Root.tsx CodeEditor test.png --props='{"code":"const x=1;","language":"javascript"}' --frame=0`
5. If test render succeeds → `REMOTION_AVAILABLE = True`

```python
REMOTION_AVAILABLE = False  # set to True after successful test render
REMOTION_DIR = f"{WORK_DIR}/remotion"
```

**If `REMOTION_AVAILABLE = False`:** visual types `diagram_animation`, `split_screen`, and `data_viz` MUST be downgraded to Playwright-rendered alternatives or replaced with a different visual type in the script. Do NOT silently fall back to `generate_image` for these types.

### Phase 1: Research

Launch 3-5 parallel subagents to investigate different angles of the topic.

See [reference/research.md](reference/research.md).

### Phase 2: Script

Convert research into a video script. **Follow the narrative arc and pacing defined in the format file.**

See [reference/scriptwriting.md](reference/scriptwriting.md) for the JSON schema and visual type guidance.

### Phase 3: Asset Production

For each segment, follow the sourcing hierarchy: search asset library, source from external APIs, then generate.

See [reference/asset-production.md](reference/asset-production.md) for the visual type → recipe router. Each visual type has a dedicated recipe file. Each sourcing channel has a dedicated recipe under `recipes/sourcing/`.

Also generate per-segment narration audio and one background music track using the `videodb` skill.

### Phase 4: Composition

Arrange all assets on a multi-track timeline. **Follow the pacing and transition rules defined in the format file.**

See [reference/composition.md](reference/composition.md).

Present the stream URL: `https://console.videodb.io/player?url={STREAM_URL}`

### Phase 4.5: Add Captions (Optional)

If the user explicitly requests captions, add speech-synced animated captions as a post-processing pass after the main stream is composed. Upload the stream, index spoken words, and recompose with a `CaptionAsset(src="auto")` overlay.

See [reference/recipes/captions.md](reference/recipes/captions.md) for the full caption config, animation styles, and color presets. **Only run this phase if the user asks for captions.**

### Phase 5: Self-Review (mandatory)

**Always runs at least once.** Upload the draft, index it, compare intended vs actual. Critique as a director.

See [reference/self-review.md](reference/self-review.md).

### Phase 6: Iterate or Deliver

If issues remain and under `MAX_ITERATIONS`, fix and recompose. Otherwise deliver the final stream URL and player URL with a segment breakdown.

## Quick Reference

| Phase | Key Reference |
|---|---|
| Format Selection | [formats/briefing.md](reference/formats/briefing.md) or [formats/fireship-explainer.md](reference/formats/fireship-explainer.md) |
| Research | [research.md](reference/research.md) |
| Script | [scriptwriting.md](reference/scriptwriting.md) |
| Asset Production | [asset-production.md](reference/asset-production.md) |
| Composition | [composition.md](reference/composition.md) |
| Self-Review | [self-review.md](reference/self-review.md) |
| Media APIs | videodb skill |

### Visual Recipe Files

| Recipe | Path |
|---|---|
| Remotion Setup | [recipes/remotion-setup.md](reference/recipes/remotion-setup.md) |
| Code Slide | [recipes/code-slide.md](reference/recipes/code-slide.md) |
| Meme & Humor | [recipes/meme-humor.md](reference/recipes/meme-humor.md) |
| Kinetic Text | [recipes/kinetic-text.md](reference/recipes/kinetic-text.md) |
| Diagram Flow | [recipes/diagram-flow.md](reference/recipes/diagram-flow.md) |
| Data Viz | [recipes/data-viz.md](reference/recipes/data-viz.md) |
| Split Compare | [recipes/split-compare.md](reference/recipes/split-compare.md) |
| Overlay Techniques | [recipes/overlay-techniques.md](reference/recipes/overlay-techniques.md) |
| Captions | [recipes/captions.md](reference/recipes/captions.md) |

### Sourcing Recipe Files

| Recipe | Path |
|---|---|
| Asset Library | [sourcing/asset-library.md](reference/recipes/sourcing/asset-library.md) |
| Stock Footage | [sourcing/stock-footage.md](reference/recipes/sourcing/stock-footage.md) |
| Meme Sourcing | [sourcing/meme-sourcing.md](reference/recipes/sourcing/meme-sourcing.md) |
| Logo Sourcing | [sourcing/logo-sourcing.md](reference/recipes/sourcing/logo-sourcing.md) |
| GIF Reactions | [sourcing/gif-reactions.md](reference/recipes/sourcing/gif-reactions.md) |
