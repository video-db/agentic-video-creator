# Captions (Auto-Synced Speech Captions)

Adds word-synced animated captions to the final video. Captions are the **last visual layer** added — they go on after all other composition is done.

## Prerequisites

The final composed video must have its spoken words indexed before captions can be applied:

```python
video.index_spoken_words(force=True)
transcript = video.get_transcript()
assert len(transcript) > 0, "No transcript — cannot add captions"
```

`src="auto"` pulls timing from the spoken-word index. No manual subtitle file needed.

## Caption Design: Fireship / Explainer Style

```python
from videodb.editor import (
    CaptionAsset, FontStyling, BorderAndShadow, Positioning,
    CaptionAlignment, CaptionAnimation,
)

caption_asset = CaptionAsset(
    src="auto",
    font=FontStyling(name="Clear Sans", size=42, bold=True),
    primary_color="&H00FFFFFF",       # white text
    secondary_color="&H00008000",     # green highlight box
    back_color="&H00000000",          # transparent background
    border=BorderAndShadow(
        outline=2,
        outline_color="&H00000000",   # black outline for readability
    ),
    position=Positioning(
        alignment=CaptionAlignment.bottom_center,
        margin_v=40,
    ),
    animation=CaptionAnimation.box_highlight,
)
```

### Why this config works

| Setting | Value | Rationale |
|---------|-------|-----------|
| Font size 42 | Large enough for 720p, not so large it competes with hero text |
| Bold | Legibility over busy backgrounds (code slides, diagrams) |
| Black outline (2px) | Guarantees readability on both light and dark backgrounds |
| `box_highlight` animation | Highlights the currently spoken word with a colored box — gives a karaoke feel that adds energy to fast narration |
| Green secondary | The highlight box color; green pops against most video backgrounds without clashing with common UI colors |
| Bottom-center, 40px margin | Standard subtitle zone; clears the lower-third area used by some overlays |
| Transparent back_color | No opaque strip — the outline handles readability, keeping the frame open |

## Animation Styles Reference

Pick the animation that matches the video's energy:

| Animation | Effect | Best for |
|-----------|--------|----------|
| `CaptionAnimation.box_highlight` | Colored box around the current word | **Fireship / explainer** — fast-paced, high-energy |
| `CaptionAnimation.color_highlight` | Current word changes color | Subtle, professional — briefings, interviews |
| `CaptionAnimation.reveal` | Words appear progressively | Slower narration, documentary feel |
| `CaptionAnimation.karaoke` | Word-by-word fill | Music videos, lyric-style |
| `CaptionAnimation.impact` | Emphasis pop on current word | Dramatic reveals, trailers |
| `CaptionAnimation.supersize` | Current word scales up | Comedy, meme-style content |

## Color Format

All colors use ASS `&HAABBGGRR` format (alpha, blue, green, red — note the reversed channel order):

```
&H00FFFFFF  → fully opaque white
&H00000000  → fully opaque black
&H00008000  → fully opaque green (R=0, G=128, B=0)
&H000000FF  → fully opaque red
&H00FF0000  → fully opaque blue
&H0000FFFF  → fully opaque yellow (R=255, G=255, B=0)
&H80000000  → 50% transparent black
```

### Color presets by format

| Format | `secondary_color` (highlight) | Vibe |
|--------|-------------------------------|------|
| Fireship explainer | `&H00008000` (green) | Terminal / hacker energy |
| Briefing | `&H00FFAA00` (light blue) | Clean, professional |
| Dark / cyberpunk | `&H000000FF` (red) | Dramatic, intense |
| Warm / creative | `&H0000CCFF` (orange) | Friendly, approachable |

## Integration into Timeline

Captions go on a **dedicated caption track** layered above the main visual and below overlays:

```python
from videodb.editor import Timeline, Track, Clip, VideoAsset

clip_duration = int(video.length)

timeline = Timeline(conn)
timeline.resolution = "1280x720"

# Track 1: main video
main_track = Track()
main_track.add_clip(0, Clip(
    asset=VideoAsset(id=video.id, start=0),
    duration=clip_duration,
))
timeline.add_track(main_track)

# Caption track: same duration, same track works too
caption_track = Track()
caption_track.add_clip(0, Clip(
    asset=caption_asset,
    duration=clip_duration,
))
timeline.add_track(caption_track)
```

Captions can also be placed on the same track as the video clip — both approaches work. Separate tracks give more control for debugging.

## Two-Pass Workflow (Recommended for Content-Creator Pipeline)

The caption step runs **after** the main video is fully composed and streamed (Phase 4 composition is done). It's a post-processing pass:

```python
# --- Phase 4 completes: stream_url is the composed video without captions ---

# Phase 4.5: Add Captions (post-composition)
print("Adding captions to final video...")

# 1. Upload the composed stream back as a single video
captioned_source = coll.upload(url=stream_url)

# 2. Index its spoken words
captioned_source.index_spoken_words(force=True)
transcript = captioned_source.get_transcript()
print(f"Indexed {len(transcript)} transcript segments")

# 3. Compose with captions
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
        position=Positioning(
            alignment=CaptionAlignment.bottom_center,
            margin_v=40,
        ),
        animation=CaptionAnimation.box_highlight,
    ),
    duration=cap_duration,
))
caption_timeline.add_track(cap_track)

captioned_stream = caption_timeline.generate_stream()
print(f"Captioned stream: {captioned_stream}")
```

This approach keeps the main composition pipeline clean and adds captions as an optional final pass.

## When to Add Captions

**Captions are OFF by default.** Only add them when the user explicitly requests it (e.g., "add captions", "with subtitles", "include captions").

| Scenario | Add captions? |
|----------|---------------|
| User explicitly requests captions | **Yes** |
| User says "with subtitles" or "captioned" | **Yes** |
| User does not mention captions | **No — skip Phase 4.5** |
| Music-only / no narration | No |

## Vertical / Square Format Adjustments

| Setting | Landscape (1280x720) | Vertical (608x1080) | Square (1080x1080) |
|---------|----------------------|----------------------|---------------------|
| Font size | 42 | 50 | 46 |
| Margin V | 40 | 60 | 50 |
| Outline | 2 | 3 | 2 |

## Quality Checks

After generating the captioned stream, verify:

- [ ] Captions are visible and readable at multiple timestamps (extract 3+ frames)
- [ ] `box_highlight` animation is active (current word has colored background)
- [ ] Captions don't overlap with Remotion-baked text in center of frame (captions are bottom-positioned, so this should be safe)
- [ ] Font size is appropriate for the output resolution
- [ ] No captions appear during silent/music-only segments (auto handles this)
