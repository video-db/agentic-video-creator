# Kinetic Text

Bold text compositions that fill the screen — stat highlights, section headers, punchy declarations, and takeaway moments. The text IS the visual.

## The Goal

Large, impactful text on a stylized background that communicates one idea instantly. Think YouTube thumbnail text but animated into a video frame. The viewer should read it in under 1 second.

## When to Use

- **Section headers:** "#1 structuredClone()" — topic intros in explainer format
- **Hook text:** "5 Features You're Missing" — opening statement
- **Stat highlights:** "73% of developers" — a number that deserves the full screen
- **Takeaways:** "Zero npm installs. All built-in." — closing punch
- **Quotes:** Key quote from research, centered and bold

## Production Approach

### Hero Moments: Remotion KineticText Component (Best — Animated)

**Use for:** hook text, section headers, takeaways, stat highlights — any text that deserves the full screen.

If `REMOTION_AVAILABLE = True`, use the KineticText component from [remotion-setup.md](remotion-setup.md). It supports `scale-in`, `slide-up`, `spring`, and `word-by-word` animations. Animated text is dramatically more impactful than a TextAsset that just appears.

```bash
npx remotion render src/Root.tsx KineticText \
  "{REMOTION_DIR}/output/kinetic_{segment_id}.mp4" \
  --props='{"lines":["5 JS Features","You Don'\''t Know"],"animation":"spring","accentColor":"#FFD700"}' \
  --width=1280 --height=720
```

Upload the `.mp4` to VideoDB as a `VideoAsset` (mute with `volume=0`).

### Quick Callouts / Lower Thirds: VideoDB TextAsset (Fast — Static)

**Use for:** data callouts, stat overlays, subtitle-style lower thirds, any text that supplements a main visual (not the main visual itself). Also use when `REMOTION_AVAILABLE = False`.

Fast, pixel-perfect, composable on the timeline. No rendering step needed.

```python
text_overlay_track.add_clip(seg_start, Clip(
    asset=TextAsset(
        text="5 JS Features\nYou're Missing",
        font=Font(family="Clear Sans", size=60, color="#FFFFFF"),
        background=Background(
            color="#000000",
            opacity=0.7,
            width=900,
            height=200,
        ),
    ),
    duration=clip_dur,
    position=Position.bottom,
    offset=Offset(y=-0.3),
))
```

### Background Layer

Kinetic text needs a background image behind it. Options:

**AI-generated atmosphere (recommended):**
```python
bg_img = coll.generate_image(
    prompt="Abstract dark technology background with subtle blue gradient, digital particles, minimalist",
    aspect_ratio="16:9",
)
visual_track.add_clip(seg_start, Clip(
    asset=ImageAsset(id=bg_img.id),
    duration=clip_dur,
    fit=Fit.crop,
))
```

**Solid dark background (fallback):**
Set `timeline.background = "#0d1117"` and don't add a visual clip — the text renders over the dark canvas.

**Reuse backgrounds:** For TextAsset kinetic text, you can reuse the same dark background if the text overlay is the star — the background is secondary. But for Remotion-rendered kinetic text, the background is baked into the video, so vary it per segment.

### Additional Animations: Custom Remotion Component

For more complex animations beyond what KineticText provides (3D rotation, morphing, particle backgrounds), write a custom Remotion component. See [remotion-setup.md](remotion-setup.md) for how to add new components.

```tsx
interface KineticTextProps {
  lines: string[];
  fontSize: number;
  staggerDelay: number;  // ms between lines appearing
  animation: "fade-up" | "scale-in" | "slide-left" | "spring";
}
```

## Style Guide

### Font Sizing (at 1280x720)

| Text role | Font size | Max words | Lines |
|-----------|-----------|-----------|-------|
| Hero stat / section header | 52-72px | 6-8 per line | 1-2 |
| Takeaway / declaration | 48-60px | 8-10 per line | 2-3 |
| Quote | 36-48px | 10-12 per line | 2-4 |
| Subtitle / attribution | 24-32px | unlimited | 1 |

### Background Bar

Every kinetic text MUST have a semi-opaque background bar:

| Parameter | Value |
|-----------|-------|
| Opacity | 0.6-0.8 |
| Width | At least 50% of frame width (900px+ at 1280w) |
| Height | Sized to text + padding |
| Color | `#000000` (black) |

### Color Accents

Use accent colors to differentiate topics:

```
Topic 1: Golden (#FFD700)
Topic 2: Red (#FF4757)
Topic 3: Blue (#3498DB)
Topic 4: Purple (#9B59B6)
Topic 5: Green (#2ECC71)
```

Apply accent color to key words or use as the font color for the topic number.

### Position

**Known gotcha:** `TextAsset` at `Position.center` with `Background` may render invisibly. Always use:

```python
position=Position.bottom,
offset=Offset(y=-0.3),  # simulates center-screen placement
```

## Making It Dynamic

Static text for 8-10 seconds feels like a PowerPoint slide. Break it up:

### Staggered lines
Show line 1 at t=0, line 2 at t=0.5s (use separate TextAsset clips offset by 0.5-1s).

### Multiple text frames
For a takeaway with 5 points, show each point one at a time (5 separate 1-2s segments) rather than all at once.

### Background variety
Alternate between 2-3 different background images across kinetic text segments.

### Pair with SFX
- **Whoosh** on section headers (topic intros)
- **Rise/swell** on stat reveals
- No SFX on takeaway (let the narration carry it)

## Duration

| Scenario | Duration |
|----------|----------|
| Section header ("#1 Feature Name") | Match narration length (typically 5-9s) |
| Hook | Match narration (typically 8-15s, can be longer for hooks) |
| Stat highlight | 3-5s (short, punchy) |
| Takeaway | Match narration (typically 6-10s) |

## NEVER Use

- `generate_image` for text — TextAsset is faster, guaranteed readable, and composable
- Tiny font sizes (below 36px for callouts, below 52px for hero stats)
- White text on a light background (always dark bg or opaque bar)
- More than 3 lines of text (if you need more, it's not kinetic text — it's something else)
