# Meme & Humor Beats

Inject comedic relief between dense content segments. Memes are 2-4 second reaction images or clips that land on a punchline — they're the pressure release valve in a fast-paced explainer.

## The Goal

A full-frame funny image or short clip that makes a developer laugh. Timed precisely to the narration's punchline. Snaps in and out with hard cuts — memes never fade.

## When to Use

- After every feature/topic explanation (the reward after learning)
- On a punchline in the narration (`humor_beat: "punchline"`)
- As a setup for a contrasting point (`humor_beat: "setup"`)
- Every 60-90 seconds in explainer format (never let humor drought exceed 90s)

## Sourcing Priority (try in order)

**Always try real memes first.** Real templates land better with developer audiences because they recognize the format.

```
1. Search asset library → recipes/sourcing/asset-library.md
2. Imgflip / Memegen.link / GIPHY / KYM → recipes/sourcing/meme-sourcing.md
3. AI generate_image (last resort — custom humor only)
```

Read [recipes/sourcing/meme-sourcing.md](sourcing/meme-sourcing.md) for full API integration details.

### When Real Memes Work Best

- Narration maps to a well-known meme format (Drake, This Is Fine, Surprised Pikachu)
- Reaction beat (facepalm, mind blown, celebration) — use GIPHY animated GIFs
- Classic developer humor with recognizable templates

### When AI Generation is OK

- Custom/unique humor concept that doesn't map to any existing template
- Very specific scene description unique to the video's topic
- All external APIs failed or returned no results

### AI Generation (Last Resort)

```python
meme_img = coll.generate_image(
    prompt=seg["visual_direction"],
    aspect_ratio="16:9",
)
```

**Prompt engineering for AI memes:**

```
[Character/subject] [doing what] [in what context], [art style], [mood/emotion]
```

| Good prompt | Why it works |
|---|---|
| "A confused developer staring at a screen full of legacy code, comic cartoon style, exaggerated expression" | Specific character, action, style |
| "A skeleton sitting on a park bench with a sign 'waiting for IE support to end', dark humor comic illustration" | Classic format adapted |

| Bad prompt | Why it fails |
|---|---|
| "funny meme about JavaScript" | Too vague |
| "drake meme" | AI can't reproduce copyrighted formats |
| "a meme" | Zero specificity |

### Fallback: Text-Based Meme

If all sourcing and generation fails, use kinetic text styled as a meme:

```python
text_asset = TextAsset(
    text="Lodash?\nNever heard of her.",
    font=Font(family="Impact", size=64, color="#FFFFFF"),
    background=Background(color="#000000", opacity=0.9, width=900, height=300),
)
```

## Timing Rules

| `humor_beat` value | Timing | Effect |
|-------------------|--------|--------|
| `"setup"` | Show meme as the setup line plays | Viewer sees the joke building |
| `"punchline"` | Flash meme exactly when the punchline lands | Maximum comedic impact |
| `None` (reaction) | Show 1-2s after the statement it reacts to | "Can you believe this?" energy |

## Composition Rules

- **Duration:** 2-3 seconds for images, 3-4 seconds for video memes
- **Transition IN:** Always `hard_cut` — memes snap onto screen
- **Transition OUT:** Always `hard_cut` — memes snap off
- **Never fade** into or out of a meme
- **Full frame** — memes don't share screen space with other visuals
- **Fit mode:** `Fit.contain` (NOT `Fit.crop`) — memes have specific aspect ratios (often square or 4:3) that must not be cropped. Use a dark background to fill the 16:9 letterbox.
- **SFX:** Pair with a comedic sting sound effect at the exact moment the meme appears

```python
# Meme segment composition — use Fit.contain to preserve aspect ratio
visual_track.add_clip(seg_start, Clip(
    asset=ImageAsset(id=meme_img.id),
    duration=clip_dur,  # 2-3 seconds
    fit=Fit.contain,
))

sfx_track.add_clip(seg_start, Clip(
    asset=AudioAsset(id=comedy_sting.id, volume=0.6),
    duration=min(1.0, float(comedy_sting.length)),
))
```

## Meme Caption Overlay (when raw template has no captions)

If you sourced a raw meme template (no Imgflip/Memegen.link captioning available), you MUST add caption text via a `TextAsset` overlay. Uncaptioned memes are contextless and the joke won't land.

```python
# Top caption (meme-style Impact font)
text_track.add_clip(seg_start, Clip(
    asset=TextAsset(
        text=top_caption.upper(),
        font=Font(family="Impact", size=48, color="#FFFFFF"),
        background=Background(color="#000000", opacity=0.0, width=1000, height=80),
    ),
    duration=clip_dur,
    position=Position.top,
    offset=Offset(y=0.05),
))

# Bottom caption
text_track.add_clip(seg_start, Clip(
    asset=TextAsset(
        text=bottom_caption.upper(),
        font=Font(family="Impact", size=48, color="#FFFFFF"),
        background=Background(color="#000000", opacity=0.0, width=1000, height=80),
    ),
    duration=clip_dur,
    position=Position.bottom,
    offset=Offset(y=-0.05),
))
```

**Caption priority:** Imgflip caption API → Memegen.link → raw template + TextAsset overlay. Never show an uncaptioned template.

## Meme Spacing

- **Minimum gap:** 15 seconds between memes (closer feels like a comedy show, not an explainer)
- **Maximum gap:** 90 seconds (audience fatigue sets in without humor relief)
- **Sweet spot:** One meme every 25-40 seconds in explainer format
- For a 3-minute video with 5 topics, that's 5 memes (one per topic, after the explanation)

## Quality Checklist

- [ ] Meme is contextually relevant to what was just said
- [ ] A developer would find it funny (not generic humor)
- [ ] Image is clear at 720p — no tiny details
- [ ] Duration is 2-3 seconds (not lingering)
- [ ] Hard cut in and out (no fades)
- [ ] Comedic sting SFX plays on appear
- [ ] Not placed back-to-back with another meme (minimum 15s gap)

## Meme as Overlay (PiP Meme)

Sometimes you want humor WITHOUT cutting away from the main visual (e.g., during a long code segment). Use a PiP meme overlay instead:

```python
overlay_track.add_clip(seg_start + 3, Clip(
    asset=ImageAsset(id=reaction_img.id),
    duration=2,
    scale=0.2,
    position=Position.bottom_right,
    offset=Offset(x=-0.05, y=-0.05),
    opacity=0.95,
))
```

See [overlay-techniques.md](overlay-techniques.md) for full PiP rules.
