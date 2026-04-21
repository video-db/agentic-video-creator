# Fireship Explainer Format

A fast-cut, information-dense tech explainer (3-7 minutes) in the style of top YouTube tech channels. Every frame carries information or humor. Dense, witty, visual, and packed with real-world assets.

## Persona

You are a fast-talking, opinionated tech creator. Think: dense information at pace with wit, visual variety every 2-5 seconds, code on screen, memes for comedic relief, and zero filler. Direct address the viewer.

**Voice characteristics:**
- Use "you" frequently — "Here's why you should care"
- Short punchy sentences — "Wrong." / "Nope." / "Here's the thing."
- Rhetorical questions — "But does that actually matter?"
- Hot takes — "Clean code is overrated." / "Most design patterns are cope."
- Specific over vague — "React 19 uses a compiler" not "modern frameworks have improvements"
- Technical but accessible — assume the viewer codes but doesn't PhD

**NEVER say:**
- "In this video, we will explore..."
- "Let me explain..."
- "As we can see..."
- "Moving on to our next topic..."
- "Without further ado..."

## Duration & Segments

| Setting | Value |
|---------|-------|
| Duration | 180-420 seconds (3-7 min) |
| Segments | 15-30+ |
| Shot duration | 2-5 seconds (rapid-fire) |
| Humor beat interval | Every 60-90 seconds |

## Narrative Arc

```
HOOK (3-5s)      → One-liner that stops the scroll. Bold claim, surprising stat, or hot take.
TOPIC 1 (15-30s) → 3-6 rapid segments covering the first point
TOPIC 2 (15-30s) → 3-6 rapid segments covering the second point
...
TOPIC N (15-30s) → 3-6 rapid segments covering the Nth point
TAKEAWAY (5-10s) → "Here's what actually matters"
CTA (3-5s)       → Subscribe, check links, etc.
```

Each topic block alternates between narration-heavy segments (code, explanation) and visual punches (memes, diagrams, logos). Never 2+ consecutive "talking head" segments without a visual interrupt.

## Pacing

| Rule | Value |
|------|-------|
| Minimum segment | 2 seconds |
| Maximum segment | 10 seconds |
| Sweet spot | 3-5 seconds |
| Hook visual-only | 0-1 seconds (immediate) |
| Browser cap maximum | 6-8 seconds |
| Code editor maximum | 8-10 seconds |
| Meme duration | 2-3 seconds |
| Dead air max | 0 seconds (NEVER) |

**Rhythm:** Fast-fast-breathe. Two rapid segments (2-4s) followed by one slightly longer (5-8s).

**Static image maximum hold time:** No single static image may appear for more than 5 seconds. If narration is longer:
- Split into two visual segments (main image 3-4s, then zoomed/cropped variant)
- Or use `generate_video` (inherent motion)
- Or use Remotion (animation built in)

## Transitions

- `hard_cut` for 80% of transitions. Segments slam into each other.
- `whip` for topic switches and energy spikes.
- `fade` sparingly — only for emotional beats or atmospheric segments.
- **Never fade into or out of a meme** — memes snap with hard_cut.

## Music & Audio

| Track | Volume |
|-------|--------|
| Narration | 1.0 |
| Background music | 0.15-0.25 (higher energy) |
| SFX | 0.4-0.7 |

Music direction: energetic, electronic, with peaks at topic transitions. Think: late-night coding session soundtrack.

SFX types:
- **Whoosh**: on hard_cut transitions between topics (0.3-0.5s)
- **Pop/click**: on stat reveals and data callouts (0.2s)
- **Comedic sting**: on meme_insert beats (0.5-1s)
- **Rise/swell**: building tension before a reveal (1-2s)

## Layering Mandate

**Every segment MUST have a base visual + at least one element of visual density.** A bare image on screen with voiceover is a slideshow, not a video. Achieve density via:

- Overlay (PiP meme, logo badge, ambient loop)
- Text element (data callout, emphasis word)
- Motion (Remotion animation, video clip, ambient loop behind static image)
- Composition (multiple logos/elements arranged on screen)

**Minimum overlays per video:** 3 (PiP memes, reaction clips, logo badges, or ambient loops).

### How to Plan Overlays (Phase 3)

During asset production, **after producing all main visuals**, make a second pass through the segment list and assign overlays:

```python
overlay_plan = []
for seg in script["segments"]:
    overlay = None
    if seg["visual_type"] == "code_editor":
        # Code slides benefit from logo badges (language/framework logo in corner)
        overlay = {"type": "logo_badge", "logo": seg.get("language", "javascript"), "position": "top_right"}
    elif seg["visual_type"] in ("image_scene", "kinetic_text") and seg.get("duration", 5) > 4:
        # Static images >4s need ambient motion underneath
        overlay = {"type": "ambient_loop", "position": "behind"}
    elif seg.get("humor_beat") and seg["visual_type"] != "meme_insert":
        # Humor beat during non-meme segment → PiP reaction in corner
        overlay = {"type": "pip_reaction", "query": "developer reaction", "position": "bottom_right"}
    if overlay:
        overlay_plan.append({"segment_id": seg["id"], **overlay})

# HARD CHECK: must have at least 3 overlays planned
assert len(overlay_plan) >= 3, f"Only {len(overlay_plan)} overlays planned — need at least 3"
```

Then produce overlay assets (logo PNGs from Simple Icons CDN, ambient loops from asset library/Pexels/generate_video, reaction GIFs from GIPHY) and place them on the overlay track during composition.

## Text Style

All text on screen follows these rules:
- **Font:** Impact, Montserrat Black, or similar thick bold sans-serif
- **Weight:** Always bold/black weight
- **Shadow:** Drop shadow (2px black) for legibility over any background
- **Optional tilt:** 2-5 degree rotation on emphasis words for energy
- **Colors:** White primary, accent color (blue/green/orange) for emphasis words
- **Size:** Hero text 52-72px, callouts 36-48px (at 1280x720)

## No Reused Backgrounds

Every segment must be visually distinct from the one before it. Hard rules:
- No two segments may share the same background image/video asset ID
- If using AI-generated backgrounds, use a **unique prompt per segment** — vary subject, color palette, and composition. Do NOT use a generic "dark tech background" prompt for multiple segments.
- Stock footage clips must be from different sources per segment
- Exception: ambient loops can repeat (they're at 20% opacity and invisible to casual viewing)

**Self-review enforcement:** During self-review, collect all visual asset IDs. If any non-ambient asset ID appears for more than one segment, that's an automatic FAIL.

```python
# During composition, track all visual asset IDs
visual_ids = {}
for seg_id, vis in visuals.items():
    aid = vis.get("id")
    if aid:
        if aid in visual_ids:
            print(f"FAIL: Asset {aid} reused in {visual_ids[aid]} AND {seg_id}")
        visual_ids[aid] = seg_id
```

## Visual Sourcing Strategy

This is what makes Fireship-style videos look professional: **real-world assets** dominate over AI-generated ones, and **Remotion animations** provide motion that VideoDB's timeline can't.

### Why Remotion is Critical for This Format

Without Remotion, you get static images with voiceover. With Remotion:
- Code **types itself** on screen (CodeEditor component)
- Diagrams **build themselves** node by node (DiagramFlow)
- Stats **count up** from zero (CounterReveal)
- Text **springs in** with physics (KineticText)
- Bars **race** to their values (BarChart)
- Topics **whip** into each other (WhipTransition)
- Comparisons **wipe reveal** (SplitCompare)

Read [recipes/remotion-setup.md](../recipes/remotion-setup.md) for all components. If `REMOTION_AVAILABLE = True`, you MUST use Remotion for at least: code_editor segments, one kinetic_text hero moment (hook or takeaway), and any diagram/data_viz/split_screen segments.

### Phase 3 (Asset Production) flow:

```
For each segment:
  1. ALWAYS read recipes/sourcing/asset-library.md → search the collection
  2. Based on visual_type:
     - stock_footage / motion_scene / image_scene → read recipes/sourcing/stock-footage.md
     - meme_insert → read recipes/sourcing/meme-sourcing.md
     - logo_composition → read recipes/sourcing/logo-sourcing.md
     - code_editor → read recipes/code-slide.md (always rendered, no external sourcing)
     - browser_capture → read reference/browser-recording.md
     - kinetic_text → read recipes/kinetic-text.md
     - diagram_animation → read recipes/diagram-flow.md
     - data_viz → read recipes/data-viz.md
     - split_screen → read recipes/split-compare.md
  3. For overlays → read recipes/sourcing/gif-reactions.md + logo-sourcing.md
  4. After producing from external source → upload to asset collection
```

### Sourcing Budget

Target for the entire video:

| Source type | Target % | Hard limit |
|---|---|---|
| Real-sourced (stock, memes, logos, screenshots) | >50% | Minimum 40% |
| AI generated (generate_image, generate_video) | <30% | Maximum 40% |
| Rendered (code, text, diagrams) | <20% | Maximum 30% |

If your video has 20 visual segments, at least 10 should use real-sourced assets (Pexels footage, Imgflip memes, GIPHY reactions, Simple Icons logos, browser captures of real websites).

### Visual type → sourcing recipe mapping

| Visual Type | First try | Then | Last resort |
|---|---|---|---|
| `stock_footage` | Asset library → Pexels video | Pixabay video | `generate_video` |
| `motion_scene` | Asset library → Pexels video | `generate_video` | — |
| `image_scene` | Asset library → Pexels photo | `generate_image` | — |
| `meme_insert` | Asset library → Imgflip/GIPHY | Memegen.link/KYM | `generate_image` |
| `logo_composition` | Simple Icons CDN / devicon | Asset library | Playwright screenshot |
| `code_editor` | (always rendered) Remotion | Playwright HTML | — |
| `browser_capture` | (always live) Playwright | — | — |
| `kinetic_text` | (always TextAsset) | — | — |
| `diagram_animation` | (always rendered) Remotion | Playwright Mermaid | — |
| `data_viz` | (always rendered) Remotion | Playwright Chart.js | — |
| `split_screen` | (always rendered) Remotion | Playwright dual | — |

## Humor Rules

- Meme every 60-90 seconds. Never exceed 90s without a humor beat.
- Memes are 2-3 seconds with hard cut in/out.
- Use REAL meme templates when possible (Imgflip, GIPHY) — they land better than AI illustrations.
- SFX comedic sting plays on meme appear.
- Memes must be contextually relevant to what was just said.
- A developer should find it funny.

## Explainer-Specific Visual Variety

- Same visual type OK for back-to-back if content differs (e.g., Python code → JS code).
- Never more than 3 consecutive segments of same type.
- Aim for type change every 2 segments.
- Minimum 5 different visual types in a full explainer.

Good sequence example:
```
hook: kinetic_text → topic1_explain: code_editor → topic1_punch: meme_insert →
topic1_evidence: browser_capture → topic2_explain: diagram_animation →
topic2_code: code_editor → topic2_meme: meme_insert → topic3_compare: split_screen →
topic3_evidence: browser_capture → takeaway: kinetic_text → cta: logo_composition
```

## Self-Review Additions (Fireship-specific)

During self-review, additionally check:
- **Sourcing budget met?** Count real-sourced vs AI-generated. Flag if AI > 40%.
- **Humor timing:** Memes land on punchlines? Gap never exceeds 90s?
- **Code readability:** Font readable at 720p? Syntax highlighting works? Characters correct?
- **Layering check:** Does every segment have at least base visual + one density element?
- **Visual variety score:** At least 5 different types used?
- **Static hold time:** No image on screen > 5 seconds?
- **Energy consistency:** One new visual every 5-7 seconds baseline maintained?
- **SFX placement:** Whooshes on transitions, pops on reveals, stings on memes?
