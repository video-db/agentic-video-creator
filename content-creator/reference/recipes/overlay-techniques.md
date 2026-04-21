# Overlay Techniques

Small visual elements that play **on top of** or **behind** the main visual on separate tracks. Overlays add motion and density without interrupting the primary content. This is one of the most powerful tools for making static images feel alive and boosting visual interest.

## The Goal

Layer 1-2 small, transient elements per segment to add motion, humor, or emphasis while the main visual stays on screen. Think YouTube face-cam or Twitch reaction overlays — small, positioned in a corner, clearly secondary to the main content.

## When to Use

| Situation | Overlay type | Why |
|-----------|-------------|-----|
| Static code screenshot held 6+ seconds | `ambient_loop` underneath | Prevents "slideshow" feel |
| Punchline during a code/diagram segment | `pip_meme` in corner | Humor without cutting away |
| Narration mentions a specific tech | `logo_badge` in corner | Visual reference |
| Key stat mentioned, main visual is something else | `stat_counter` text | Flash the number |
| Any static image segment > 5 seconds | `ambient_loop` at low opacity | Subtle motion makes it feel alive |

## How Overlays Work on the Timeline

Overlays use VideoDB's `scale`, `position`, `offset`, and `opacity` clip properties on a separate track that renders above (or below) the main visual.

```python
# Main visual — full screen
main_track = Track()
main_track.add_clip(10, Clip(
    asset=ImageAsset(id=code_img.id),
    duration=8,
    fit=Fit.crop,
))

# Small reaction image in bottom-right corner
overlay_track = Track()
overlay_track.add_clip(13, Clip(     # appears 3s into the segment
    asset=ImageAsset(id=reaction.id),
    duration=2,                       # visible for 2 seconds
    scale=0.2,
    position=Position.bottom_right,
    offset=Offset(x=-0.05, y=-0.05),
    opacity=0.95,
))

# overlay_track added AFTER main_track → renders on top
timeline.add_track(main_track)
timeline.add_track(overlay_track)
```

## Overlay Types

### PiP Meme / Reaction

A small funny image or animated GIF in the corner during a content segment.

**Source with:** Real reaction GIFs from GIPHY (see [sourcing/gif-reactions.md](sourcing/gif-reactions.md)) or real meme templates from Imgflip (see [sourcing/meme-sourcing.md](sourcing/meme-sourcing.md)). Fall back to `generate_image` only if APIs unavailable.

```python
# Using a real GIPHY reaction (preferred)
overlay_track.add_clip(seg_start + 3, Clip(
    asset=VideoAsset(id=gif_asset.id, volume=0),
    duration=min(2, math.floor(float(gif_asset.length) * 100) / 100),
    scale=0.20,
    position=Position.bottom_right,
    offset=Offset(x=-0.05, y=-0.05),
    opacity=0.95,
))

# Fallback: AI-generated static image
overlay_track.add_clip(seg_start + 3, Clip(
    asset=ImageAsset(id=meme_img.id),
    duration=2,
    scale=0.20,
    position=Position.bottom_right,
    offset=Offset(x=-0.05, y=-0.05),
    opacity=0.95,
))
```

### Reaction Video Clip

A short animated clip (facepalm, celebration, confusion) in the corner. Real GIFs are more impactful.

**Source with:** GIPHY API (see [sourcing/gif-reactions.md](sourcing/gif-reactions.md)).

```python
# Search for appropriate reaction
gifs = search_reaction_gifs("facepalm developer")
gif_asset = download_gif_as_video(gifs[0], WORK_DIR, asset_coll)

overlay_track.add_clip(seg_start + 2, Clip(
    asset=VideoAsset(id=gif_asset.id, volume=0),
    duration=min(3, math.floor(float(gif_asset.length) * 100) / 100),
    scale=0.18,
    position=Position.bottom_right,
    offset=Offset(x=-0.05, y=-0.05),
    opacity=0.9,
))
```

### Logo Badge

Real tech logo in a corner while the main visual is code or a diagram.

**Source with:** Simple Icons CDN (see [sourcing/logo-sourcing.md](sourcing/logo-sourcing.md)). Never AI-generate logos.

```python
# Download real logo from Simple Icons CDN
logo_path = download_logo_as_png("javascript", WORK_DIR, size=128)
logo_asset = asset_coll.upload(file_path=logo_path, name="simpleicons_javascript_logo")

overlay_track.add_clip(seg_start, Clip(
    asset=ImageAsset(id=logo_asset.id),
    duration=clip_dur,
    scale=0.08,
    position=Position.top_right,
    offset=Offset(x=-0.03, y=0.03),
    opacity=0.85,
))
```

### Ambient Loop (Background Motion)

A short video looped at very low opacity BEHIND the main visual. Makes static images feel alive.

**Source with:** Search asset library for existing ambient clips, or search Pexels for abstract/particle videos (see [sourcing/stock-footage.md](sourcing/stock-footage.md)). Fall back to `generate_video` if no stock found.

```python
# Try: search Pexels for ambient footage
ambient_results = search_pexels_videos("abstract particles dark background")
if ambient_results:
    ambient = download_and_upload_video(
        ambient_results[0]["url"], "pexels_ambient_particles", asset_coll, WORK_DIR
    )
else:
    # Fallback: AI generate
    ambient = coll.generate_video(
        prompt="Subtle digital particles floating slowly, dark background, abstract tech atmosphere",
    )

# Place BELOW the main visual track
ambient_track = Track()
anim_len = math.floor(float(ambient.length) * 100) / 100
loops = math.ceil(seg_duration / anim_len)

for i in range(loops):
    loop_start = seg_start + int(i * anim_len)
    remaining = (seg_start + seg_duration) - loop_start
    if remaining > 0:
        ambient_track.add_clip(loop_start, Clip(
            asset=VideoAsset(id=ambient.id, volume=0),
            duration=min(anim_len, remaining),
            opacity=0.20,
        ))

# Add BEFORE main visual track so it renders behind
timeline.add_track(ambient_track)
timeline.add_track(main_track)
```

### Stat Counter

A TextAsset showing a key number while the main visual is something else.

```python
stat_track.add_clip(seg_start + 1, Clip(
    asset=TextAsset(
        text="73%",
        font=Font(family="Clear Sans", size=36, color="#61DAFB"),
        background=Background(color="#000000", opacity=0.7, width=200, height=60),
    ),
    duration=3,
    position=Position.top_left,
    offset=Offset(x=0.05, y=0.05),
))
```

## Placement Rules

| Parameter | Guideline |
|-----------|-----------|
| **Scale** | `0.15-0.25` for most overlays. `0.08-0.12` for logo badges. `1.0` for ambient loops (full-screen behind). |
| **Position** | Most overlays go to `bottom_right` or `top_right`. Keep out of the main content area. |
| **Offset** | `Offset(x=-0.05, y=-0.05)` for slight inward padding. Flush against edge looks accidental. |
| **Opacity** | `0.85-0.95` for PiP and reactions. `0.15-0.25` for ambient loops. |
| **Duration** | 2-4 seconds for PiP/reactions. Full segment for logos and ambient loops. |
| **Volume** | Always `volume=0` on video overlays. Only narration + music + SFX produce sound. |

## Timing Pattern

```python
# Overlay appears partway into the segment, not at the start
overlay_start = seg_start + 2    # 2 seconds after segment begins
overlay_duration = 3             # visible for 3 seconds

# This gives the viewer time to register the main visual
# before the overlay draws their eye to the corner
```

## Limits

- **Max 2 overlays per segment.** More = visual clutter.
- **3-5 total overlays per explainer video.** Overlays are spice, not the meal.
- **NEVER overlay on `kinetic_text` segments.** The text IS the visual.
- **NEVER overlay on `meme_insert` segments.** The meme IS the content.
- **Scale > 0.3 competes with the main visual.** Keep it small.

## Production Tips

- Generate overlay assets in the same batch as main visuals — they're quick to produce.
- Reuse one ambient loop video across multiple segments (loop it).
- PiP memes should be contextually relevant to what's on screen, not random.
- If a segment has both a logo badge and a PiP meme, stagger them: logo at start, meme at second 3.

## Track Order (Critical)

```
timeline.add_track(ambient_track)       # renders BEHIND main visual
timeline.add_track(main_visual_track)   # base layer
timeline.add_track(text_overlay_track)  # text on top of visual
timeline.add_track(pip_overlay_track)   # PiP images/videos on top
timeline.add_track(narration_track)     # audio
timeline.add_track(sfx_track)           # audio
timeline.add_track(music_track)         # audio
```

Tracks added later render on top. Ambient goes first (behind). PiP overlays go after the main visual (on top).
