# Composition

How to arrange assets on the timeline. These are editorial rules — what makes a video feel produced, not assembled. Use the `videodb` skill for all timeline API operations. **Read your format file for format-specific pacing and transition rules.**

## Track Architecture

Build the video on multiple tracks, layered bottom to top:

```
Track N (top)    → Overlay clips: PiP memes, reaction videos, logo badges (scale 0.15-0.25)
Track 6          → SFX (AudioAsset: whooshes, pops, comedic stings) [explainer only]
Track 5          → Data call-outs, lower thirds (TextAsset)
Track 4          → Captions / subtitles (CaptionAsset)
Track 3          → Title card, outro card (TextAsset)
Track 2          → Narration audio (AudioAsset, volume=1.0)
Track 1 (bottom) → Visual content (VideoAsset / ImageAsset per segment)
Track 0          → Ambient loops (VideoAsset, opacity=0.15-0.25) [optional, under main visual]
+ Separate track  → Background music (AudioAsset, volume=0.1-0.25)
```

Visual content is the base layer. Everything else overlays on top. Audio tracks (narration + music + SFX) mix together — narration at full volume, music underneath, SFX as punctuation.

## Transition Types

| Type | Effect | Use When |
|------|--------|----------|
| `hard_cut` | Instant switch, no blend | Default for fireship-explainer. High energy. Between any two rapid segments. |
| `fade` | 0.5s cross-dissolve | Default for briefing. Between visually different segments that need smoothing. |
| `whip` | Fast horizontal wipe (0.2-0.3s) | Topic switches in explainer. Energy spikes. Before/after meme beats. |
| `graphic` | Custom graphic transition | Section breaks. Between major topics in explainer. |

**Transition defaults are defined in your format file.** Read it for format-specific transition rules.

Implementation: Use `Transition(in_="fade", out="fade", duration=0.5)` for fades. For hard_cut, simply don't add a transition (clips abut directly). For whip/graphic transitions, use a pre-rendered Remotion clip:

```python
# Pre-render whip transitions during asset production (one per direction is enough)
# See recipes/remotion-setup.md for the WhipTransition component
if REMOTION_AVAILABLE:
    # Render a 0.5s whip transition clip
    os.system(f'cd {REMOTION_DIR} && npx remotion render src/Root.tsx WhipTransition '
              f'{REMOTION_DIR}/output/whip_right.mp4 '
              f'--props=\'{{"direction":"right","color":"#3498DB"}}\' '
              f'--width=1280 --height=720')
    whip_clip = coll.upload(file_path=f"{REMOTION_DIR}/output/whip_right.mp4")

# Insert whip between topic segments on an overlay track
transition_track.add_clip(topic_switch_time, Clip(
    asset=VideoAsset(id=whip_clip.id, volume=0),
    duration=math.floor(float(whip_clip.length) * 100) / 100,
    opacity=0.8,
))
```

## Structure Rules

**Read your format file** (`reference/formats/*.md`) for format-specific structure rules (opening, between segments, outro). Here's the universal guidance:

### All Formats

**Opening:**
- Start with visual before narration begins (1-3s visual-only lead).
- Title card overlays the hook visual.

**Outro:**
- Last visual has clean ending.
- Outro text card appears after final narration ends (3-5 seconds).
- Music fades out over final 3 seconds.

### Format-Specific (read your format file for full details)

**Briefing:** Fades between segments, 2-3s visual lead before narration, smooth transitions.

**Fireship Explainer:** Hard cuts everywhere, segments slam into each other, memes snap in/out, SFX sting on humor beats, 0-1s before narration starts.

## Pacing Rules

**Full pacing tables are in your format file.** Here's the universal guidance:

### Universal Rules

| Rule | Value |
|------|-------|
| Clip duration | Never exceed source asset `.length` |
| Duration truncation | `math.floor(length * 100) / 100` |
| Dead air | Minimize (briefing: 1s max; explainer: never) |
| Static image hold | Max 5 seconds (split, add motion, or cut) |

### Format-Specific Summary

**Briefing:** 8-20s segments, sweet spot 12-15s. Vary lengths: short-long-short. 2-3s visual before narration.

**Fireship Explainer:** 2-10s segments, sweet spot 3-5s. Fast-fast-breathe rhythm. One new visual every 4-7 seconds. If any visual lingers beyond 10 seconds, the viewer feels the pace drop.

**Static image maximum hold time (all formats):** No single static image may appear on screen for more than 5 seconds. If narration is longer:
- Split into two visual segments
- Use `generate_video` (inherent motion)
- Use Remotion (animation built in)
- Add an ambient loop overlay at 0.2 opacity

## Audio Mixing

**Narration (Track 2):**
- Volume: 1.0 (full). Primary audio.
- Start timing depends on format (read format file).
- End narration 2-3 seconds before video ends (outro breathes).

**Background music (separate track):**
- Briefing volume: 0.1-0.2
- Explainer volume: 0.15-0.25 (slightly higher energy)
- Spans full video duration. Loop if `generate_music()` returned shorter audio.
- Fades out over last 3 seconds.

**SFX (explainer formats only):**
- Volume: 0.4-0.7 (louder than music, softer than narration)
- Types:
  - **Whoosh**: on hard_cut transitions between topics (0.3-0.5s)
  - **Pop/click**: on stat reveals and data callouts (0.2s)
  - **Comedic sting**: on meme_insert beats (0.5-1s)
  - **Rise/swell**: building tension before a reveal (1-2s)
- Each SFX is a separate AudioAsset placed at the exact timestamp

**Visual assets with audio:**
- AI-generated video clips: mute (volume=0)
- Browser captures: mute unless audio is intentionally part of the story
- Stock footage: always mute

## Zoom and Pan (Explainer Format)

VideoDB's timeline editor doesn't support zoom/pan natively. To achieve zoom or pan effects:

1. **Pre-process with Remotion**: Render the zoom/pan as part of the Remotion component (e.g., code editor that zooms into a function). The output video already contains the motion.
2. **Crop in browser capture**: Use Playwright's viewport settings to capture a zoomed-in portion of the screen.
3. **Generate zoomed variants**: For AI images, generate two versions (wide and zoomed) and cut between them.

Never try to apply zoom/pan at the timeline level — it's not supported.

## Format Rules

**Landscape (default, 16:9):**
- Resolution: `1280x720`
- Text sizes: title 48-60px, data call-outs 36-48px, captions 30px

**Vertical (9:16):**
- Resolution: `608x1080`
- Text sizes: increase by 20% from landscape values

**Square (1:1):**
- Resolution: `1080x1080`
- Compromise between landscape and vertical rules

## Timeline Gotchas

These are hard constraints from the VideoDB Editor API. Violating them causes `InvalidRequestError`.

**Clip duration must never exceed source asset length:**
- `Clip(asset=VideoAsset(id=v.id), duration=15)` will fail if the video is only 8s.
- Always store exact `.length` and use it as a ceiling.

**Always floor durations, never round:**
- Use `math.floor(length * 100) / 100` to truncate to 2 decimal places.

**`.length` may return a string:**
- Always cast: `float(asset.length)` before using in arithmetic.

**`Track.add_clip(start, clip)` — start is an integer:**
- Plan segment boundaries at whole-second marks.

**`generate_music()` may return shorter audio than requested:**
- Always check `music.length` after generation. Loop if shorter than video.

**AI-generated videos are 5-8 seconds max:**
- Never set clip duration beyond video's actual length.

## Remotion-Rendered Segments: No TextAsset Overlays

**CRITICAL RULE:** When a segment's main visual is a Remotion-rendered video (CodeEditor, KineticText, DiagramFlow, BarChart, SplitCompare, CounterReveal), that video already contains text baked into its frames. **Do NOT add any `TextAsset` overlay (data callout, emphasis text, subtitle) on top of it.** Doing so produces ugly double-text where VideoDB's TextAsset renders on top of Remotion's baked-in text.

```python
# During composition, track which segments used Remotion
REMOTION_VISUAL_TYPES = {"code_editor", "kinetic_text", "diagram_animation", "data_viz", "split_screen"}

def segment_is_remotion(seg):
    """Check if this segment's visual was produced by Remotion."""
    return (seg.get("production_method") == "remotion" or
            (REMOTION_AVAILABLE and seg.get("visual_type") in REMOTION_VISUAL_TYPES))

# When placing text overlays / data callouts:
for seg in script["segments"]:
    if segment_is_remotion(seg):
        # SKIP text overlays — Remotion video already has text baked in
        continue
    # ... add TextAsset clips only for non-Remotion segments ...
```

**What IS allowed on Remotion segments:**
- Logo badges (small, corner-positioned, don't overlap text) — `scale 0.08, Position.top_right`
- Ambient loops underneath (they render behind, not on top)
- SFX audio clips (audio doesn't overlap visually)

**What is BANNED on Remotion segments:**
- `TextAsset` data callouts
- `TextAsset` emphasis/hero text
- `TextAsset` title overlays
- Any `TextAsset` that would render text on top of the video's existing text

## Narration Audio Continuity

**CRITICAL RULE:** Narration audio must play continuously across the video with no gaps or overlaps at segment boundaries. Audio drops during transitions are caused by:

1. **Gaps between narration clips:** Segment N's narration ends at t=10.2s but segment N+1's narration starts at t=11.0s → 0.8s of silence.
2. **Overlapping narration clips:** Two narration clips placed at overlapping timestamps → one gets suppressed.

### How to prevent audio drops

```python
# Build narration as a continuous chain — each clip starts exactly where the previous one ended.
narration_track = Track()
narration_cursor = 0  # running position in seconds

for seg in script["segments"]:
    voice = voice_assets[seg["id"]]
    voice_len = math.floor(float(voice.length) * 100) / 100

    # Place narration at the current cursor position (integer start)
    start = int(narration_cursor)
    narration_track.add_clip(start, Clip(
        asset=AudioAsset(id=voice.id),
        duration=voice_len,
    ))

    # Advance cursor by the exact voice duration (not segment visual duration)
    narration_cursor = start + voice_len

# The visual track should be aligned to the same segment boundaries.
# Use narration_cursor positions as the authoritative timeline for visuals too.
```

### Key rules:
- **Narration is the master clock.** Segment boundaries are defined by narration timing, not visual asset lengths.
- **No gaps:** Each narration clip starts exactly at `int(previous_end)`. If previous ends at 10.3s, next starts at 10.
- **No overlaps:** Never place two narration clips that would overlap in time.
- **Visual clips fill to match:** Each visual segment's duration is set to match its narration duration (or slightly exceed it for visual breathing room at the end of the video).

## Overlay Composition (Picture-in-Picture)

VideoDB supports simultaneous clips on different tracks with `scale`, `position`, `offset`, and `opacity`. This enables picture-in-picture overlays — small visual elements that play on top of the main visual.

### Track architecture with overlays

```
Track 8 (top)    → Overlay clips (small images/videos, scaled down)
Track 7          → SFX (AudioAsset: whooshes, pops, stings)
Track 6          → Data call-outs, lower thirds (TextAsset)
Track 5          → Captions / subtitles (CaptionAsset)
Track 4          → Title card, outro card (TextAsset)
Track 3          → Narration audio (AudioAsset, volume=1.0)
Track 2          → Ambient loops (VideoAsset, full-screen, opacity=0.15-0.25)
Track 1 (bottom) → Main visual content (VideoAsset / ImageAsset per segment)
+ Separate track  → Background music (AudioAsset, volume=0.1-0.25)
```

### Overlay placement rules

**Position:** Use the 9-zone grid (`Position.top_left` through `Position.bottom_right`). Most overlays go to `bottom_right` or `top_right` — out of the way of the main content.

**Scale:** `0.15-0.25` for most overlays. The overlay should be noticeable but not competing with the main visual. Think YouTube face-cam size.

**Offset:** Use `Offset(x=-0.05, y=-0.05)` to add slight inward padding from the edge. Clips flush against the frame edge look accidental.

**Opacity:** `0.85-0.95` for PiP memes and reactions. `0.15-0.25` for ambient loops (they should be felt, not seen).

**Duration:** Overlays are transient — 2-4 seconds. They pop in, add visual interest, and disappear. Exception: ambient loops and logo badges which can span the full segment.

**Volume:** Always `volume=0` on video overlays. Only narration, music, and SFX produce sound.

### Overlay timing

```python
# Overlay appears 2 seconds into the segment, lasts 3 seconds
seg_start = 10  # segment starts at t=10
overlay_start = seg_start + 2  # overlay appears at t=12
overlay_duration = 3  # disappears at t=15

overlay_track.add_clip(overlay_start, Clip(
    asset=VideoAsset(id=reaction.id, volume=0),
    duration=min(overlay_duration, float(reaction.length)),
    scale=0.2,
    position=Position.bottom_right,
    offset=Offset(x=-0.05, y=-0.05),
    opacity=0.9,
))
```

### Looping ambient animations

Short AI videos (2-3s) can be looped to create continuous subtle motion behind static images:

```python
ambient_track = Track()
anim_len = math.floor(float(ambient.length) * 100) / 100
seg_duration = 8  # seconds this segment lasts

loops = math.ceil(seg_duration / anim_len)
for i in range(loops):
    loop_start = seg_start + int(i * anim_len)
    remaining = (seg_start + seg_duration) - loop_start
    if remaining > 0:
        ambient_track.add_clip(loop_start, Clip(
            asset=VideoAsset(id=ambient.id, volume=0),
            duration=min(anim_len, remaining),
            opacity=0.2,  # very subtle — viewer feels motion, doesn't see it
        ))
```

Place `ambient_track` BELOW the main visual track so it renders behind it. If the main visual is a static image, the ambient video's motion will bleed through at low opacity, giving the frame a living quality.

### When to use overlays

| Situation | Overlay technique |
|-----------|------------------|
| Static code screenshot on screen for 8+ seconds | Add `ambient_loop` underneath + `pip_meme` reaction at second 4 |
| Narration mentions a specific tech while diagram is on screen | `logo_badge` of that tech in corner |
| Punchline during a code segment (don't want to cut away) | `pip_meme` in bottom-right for 2 seconds |
| Stat mentioned but main visual is a browser capture | `stat_counter` TextAsset in top-left |
| Any segment with a static image longer than 5 seconds | `ambient_loop` at opacity 0.2 to add subtle motion |

### Overlay limits

- **Max 2 overlays per segment.** More than that clutters the frame.
- **3-5 total overlays per explainer video.** They're spice, not the meal.
- **Never overlay TextAsset on Remotion-rendered segments.** Remotion videos have text baked in — adding TextAsset creates ugly double-text. Logo badges (small, corner) are OK.
- **Never overlay on top of kinetic_text segments.** The text IS the visual — don't compete with it.
- **Never overlay on meme_insert segments.** The meme IS the content.

### Building the overlay track from the plan (Phase 4)

During composition, read `{WORK_DIR}/scripts/overlay_plan.json` (produced in Phase 3) and place each overlay on the overlay track:

```python
import json

with open(f"{WORK_DIR}/scripts/overlay_plan.json") as f:
    overlay_plan = json.load(f)
with open(f"{WORK_DIR}/scripts/overlay_assets.json") as f:
    overlay_assets = json.load(f)  # {segment_id: {id, type, length}}

overlay_track = Track()
overlay_count = 0

for entry in overlay_plan:
    sid = entry["segment_id"]
    seg_start = segment_starts[sid]  # from your segment timing dict
    seg_dur = segment_durations[sid]
    asset_info = overlay_assets.get(sid)
    if not asset_info:
        continue

    if entry["type"] == "logo_badge":
        overlay_track.add_clip(seg_start, Clip(
            asset=ImageAsset(id=asset_info["id"]),
            duration=min(seg_dur, 8),
            scale=entry.get("scale", 0.08),
            position=Position.top_right,
            offset=Offset(x=-0.03, y=0.03),
            opacity=0.85,
        ))
        overlay_count += 1

    elif entry["type"] == "pip_reaction":
        delay = min(2, seg_dur // 3)
        if asset_info.get("is_video"):
            overlay_track.add_clip(seg_start + delay, Clip(
                asset=VideoAsset(id=asset_info["id"], volume=0),
                duration=min(3, math.floor(float(asset_info["length"]) * 100) / 100),
                scale=entry.get("scale", 0.20),
                position=Position.bottom_right,
                offset=Offset(x=-0.05, y=-0.05),
                opacity=0.9,
            ))
        else:
            overlay_track.add_clip(seg_start + delay, Clip(
                asset=ImageAsset(id=asset_info["id"]),
                duration=3,
                scale=entry.get("scale", 0.20),
                position=Position.bottom_right,
                offset=Offset(x=-0.05, y=-0.05),
                opacity=0.9,
            ))
        overlay_count += 1

    elif entry["type"] == "stat_counter":
        overlay_track.add_clip(seg_start + 1, Clip(
            asset=TextAsset(
                text=entry["text"],
                font=Font(family="Clear Sans", size=36, color=entry.get("color", "#61DAFB")),
                background=Background(color="#000000", opacity=0.7, width=250, height=60),
            ),
            duration=min(4, seg_dur - 1),
            position=Position.top_left,
            offset=Offset(x=0.05, y=0.05),
        ))
        overlay_count += 1

# HARD CHECK before generating stream
assert overlay_count >= 3, f"FAIL: Only {overlay_count} overlays placed — need at least 3"
print(f"Placed {overlay_count} overlays on overlay track")

# Add overlay track AFTER main visual track (renders on top)
timeline.add_track(overlay_track)
```

## Phase 4.5: Add Captions (Optional — User-Requested Only)

**Captions are OFF by default.** Only run this phase if the user explicitly asks for captions (e.g., "add captions", "with subtitles", "include captions").

After the main timeline stream is generated, add speech-synced captions as a final pass. See [recipes/captions.md](recipes/captions.md) for full config, animation styles, and color presets.

```python
from videodb.editor import (
    CaptionAsset, FontStyling, BorderAndShadow, Positioning,
    CaptionAlignment, CaptionAnimation,
)

captioned_source = coll.upload(url=stream_url)
captioned_source.index_spoken_words(force=True)
transcript = captioned_source.get_transcript()
print(f"Indexed {len(transcript)} transcript segments for captions")

caption_timeline = Timeline(conn)
caption_timeline.resolution = "1280x720"

cap_track = Track()
cap_duration = int(captioned_source.length)
cap_track.add_clip(0, Clip(
    asset=VideoAsset(id=captioned_source.id, start=0),
    duration=cap_duration,
))
cap_track.add_clip(0, Clip(
    asset=CaptionAsset(
        src="auto",
        font=FontStyling(name="Clear Sans", size=42, bold=True),
        primary_color="&H00FFFFFF",
        secondary_color="&H00008000",
        back_color="&H00000000",
        border=BorderAndShadow(outline=2, outline_color="&H00000000"),
        position=Positioning(alignment=CaptionAlignment.bottom_center, margin_v=40),
        animation=CaptionAnimation.box_highlight,
    ),
    duration=cap_duration,
))
caption_timeline.add_track(cap_track)

captioned_stream = caption_timeline.generate_stream()
stream_url = captioned_stream  # replace with captioned version
```

Captions are **off by default**. Only add them when the user explicitly requests captions/subtitles.

## Checklist Before Generating Stream

Before calling `timeline.generate_stream()`, verify:

- [ ] No clip duration exceeds its source asset's actual `.length` (floor, don't round)
- [ ] Transitions match the format (hard_cut for explainer, fade for briefing)
- [ ] No two consecutive segments use the same visual type (briefing) or more than 3 in a row (explainer)
- [ ] Data call-outs appear after narration mentions them, not before
- [ ] Music track spans full duration at correct volume (loop if needed)
- [ ] All video/capture assets are muted (volume=0)
- [ ] Narration ends before outro card appears
- [ ] Outro card is 3-5 seconds
- [ ] Total duration within TARGET_DURATION range for format
- [ ] All `add_clip(start, ...)` start values are integers
- [ ] All text overlays meet minimum font size (36px callouts, 52px hero stats)
- [ ] No `Position.center` + `Background` combo on TextAssets
- [ ] Every callout has semi-opaque background bar (opacity 0.6+)
- [ ] SFX placed at correct timestamps (explainer only)
- [ ] Meme segments are exactly 2-3 seconds with hard_cut in/out
- [ ] Meme segments use `Fit.contain` (NOT `Fit.crop`) — memes have non-16:9 aspect ratios
- [ ] Meme segments have caption text (TextAsset overlay) if raw template was used without API captioning
- [ ] Overlay clips use `scale` 0.15-0.25 (not full screen unless ambient)
- [ ] All overlay video clips are muted (volume=0)
- [ ] Overlay track added AFTER main visual track (renders on top)
- [ ] Ambient loop track added BEFORE main visual track (renders behind)
- [ ] No more than 2 overlays per segment, 3-5 per video total
- [ ] At least 3 overlay clips placed (logo badges, PiP memes, ambient loops) for explainer format
- [ ] Meme segments have caption text if raw template was used
- [ ] **NO TextAsset placed on any Remotion-rendered segment** (code_editor, kinetic_text, diagram, data_viz, split_screen) — Remotion videos already contain baked-in text
- [ ] Narration clips chain continuously — no gaps or overlaps between consecutive narration clips
- [ ] Visual segment durations match narration durations (narration is the master clock)
- [ ] **Captions** (Phase 4.5) — only if user requested: `index_spoken_words` + `CaptionAsset(src="auto")` with `box_highlight` animation
