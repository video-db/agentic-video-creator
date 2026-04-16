# Composition

How to arrange assets on the timeline. These are editorial rules — what makes a video briefing feel produced, not assembled. Use the `videodb` skill for all timeline API operations.

## Track Architecture

Build the video on 5 tracks, layered bottom to top:

```
Track 5 (top)    → Data call-outs, lower thirds (TextAsset)
Track 4          → Captions / subtitles (CaptionAsset)
Track 3          → Title card, outro card (TextAsset)
Track 2          → Narration audio (AudioAsset, volume=1.0)
Track 1 (bottom) → Visual content (VideoAsset / ImageAsset per segment)
+ Separate track  → Background music (AudioAsset, volume=0.1-0.2)
```

Visual content is the base layer. Everything else overlays on top. Audio tracks (narration + music) mix together — narration at full volume, music underneath.

## Structure Rules

**Opening (first 3 seconds):**
- Start with motion before the narration begins. The viewer should see something moving before they hear anything.
- If the hook is a `motion_scene`, let it play for 2-3 seconds before narration starts. The narration clip starts at t=2 or t=3, not t=0.
- Title card fades in over the hook visual, not on a blank screen.

**Between segments:**
- 0.5-1.0 second fade transitions between visual clips. Use `Transition(in_="fade", out="fade", duration=0.5)`.
- Don't hard-cut between visually different segments — the fade gives the viewer's eye a moment to adjust.
- Exception: kinetic_text to kinetic_text can hard-cut if the energy calls for it.

**Data call-outs:**
- Appear 0.5 seconds AFTER the narration mentions the stat. The viewer hears the number, then sees it.
- Stay on screen for 3-4 seconds minimum so the viewer can read it.
- Fade in, don't pop in.
- Position at bottom-center or bottom-left. Never in the center of the frame — that's where the main visual lives.
- **Size matters more than you think.** Call-outs must be large enough to notice in a 1-second glance at 1x playback speed. A viewer will not pause to read tiny text — if they can't catch it while the video plays, it doesn't exist.
- Font size >= 36px for standard callouts, >= 52px for hero stats. Background bar must span at least 30% of frame width.
- **Screenshot test:** If someone screenshots this frame and posts it on Twitter, would the callout text be readable and look intentional? If it looks like an afterthought or a debug label, increase the size.
- Avoid thin, single-line callouts that blend into the visual — they vanish at normal playback speed. A callout should feel like a broadcast lower-third, not a subtitle.

**Outro:**
- The last visual segment should have a fade-out transition.
- Outro text card appears after the final narration ends, not during it.
- Keep it to 3-5 seconds. A clean "end" is better than a lingering one.
- Background music should fade out over the final 3 seconds of the video.

## Pacing Rules

**Segment durations:**
- Minimum: 8 seconds (anything shorter feels like a flash)
- Maximum: 20 seconds (anything longer risks losing attention)
- Sweet spot: 12-15 seconds for most insight segments

**Rhythm:**
- Vary segment lengths. Short-long-short creates energy.
- The most important insight gets the longest segment.
- Place the shortest segment right before the takeaway — it creates a "breath" before the conclusion.

**Browser capture segments:**
- Cap at 10-15 seconds. Screen recordings lose attention faster than other visual types.
- The narration should start immediately — don't let the viewer watch a browser loading in silence.

**Dead air:**
- Never have more than 1 second without narration OR music. If there's a natural pause in narration, the music fills the gap.
- Between segments, a short music-only moment (1-2 seconds) can work as a transition.

## Audio Mixing

**Narration (Track 2):**
- Volume: 1.0 (full). This is the primary audio.
- Start narration 2-3 seconds after the video starts (let the hook visual breathe).
- End narration 2-3 seconds before the video ends (let the outro breathe).

**Background music (separate track):**
- Volume: 0.1-0.2. It should be felt, not heard. If someone asks "is there music?" and they're not sure, the level is right.
- Spans the full video duration.
- Fades out over the last 3 seconds.
- The music_direction from the script guides what kind of music to generate.

**Visual assets with audio:**
- AI-generated video clips (`generate_video`) may have their own audio. Mute them (volume=0) — your narration and music replace it.
- Browser capture recordings will have system audio. Mute them too unless the audio is intentionally part of the story.

## Format Rules

**Landscape (default, 16:9):**
- Resolution: `1280x720`
- Good for: demo screens, presentations, YouTube, conference talks
- Text sizes: title 48-60px, data call-outs 36-48px, captions 30px
- Data call-outs at bottom-center work well

**Vertical (9:16):**
- Resolution: `608x1080`
- Good for: TikTok, Reels, Shorts, mobile-first audiences
- Text sizes: increase by 20% from landscape values
- Data call-outs move to center-screen (more vertical space to use)
- Captions move to upper-center (thumb zone at bottom)

**Square (1:1):**
- Resolution: `1080x1080`
- Good for: Instagram feed, LinkedIn, Twitter/X
- Compromise between landscape and vertical rules

## Timeline Gotchas

These are hard constraints from the VideoDB Editor API. Violating them causes `InvalidRequestError`.

**Clip duration must never exceed source asset length:**
- `Clip(asset=VideoAsset(id=v.id), duration=15)` will fail if the video is only 8s.
- `Clip(asset=AudioAsset(id=a.id), duration=19.49)` will fail if the audio is 19.487s.
- Always store the exact `.length` returned at generation time and use it as a ceiling.

**Always floor durations, never round:**
- Use `math.floor(length * 100) / 100` to truncate to 2 decimal places.
- `round()` can round up (e.g., 19.487 → 19.49), which exceeds the actual asset length by fractions of a second — enough to fail.

**`.length` may return a string:**
- `voice.length`, `music.length`, `video.length` may return strings, not floats.
- Always cast: `float(asset.length)` before using in arithmetic or comparisons.

**`Track.add_clip(start, clip)` — start is an integer:**
- The `start` parameter only accepts whole seconds. Sub-second precision is lost.
- Plan segment boundaries at whole-second marks to avoid timing drift between narration and visuals.

**`generate_music()` may return shorter audio than requested:**
- Requesting 90s may yield 30s. Always check `music.length` after generation.
- If shorter than the video, loop by placing multiple `AudioAsset` clips at staggered start times on the music track (e.g., t=0, t=music_length, t=2*music_length).

**AI-generated videos are 5-8 seconds max:**
- `generate_video()` produces clips of 5-8s. If a segment is longer (e.g., 13s hook with 2s breathing + 11s narration), the clip won't cover it.
- Never set clip duration beyond the video's actual length. Instead, start the next segment's visual early to fill the gap, or generate an additional image to cover the remaining time.

## Checklist Before Generating Stream

Before calling `timeline.generate_stream()`, verify:

- [ ] **No clip duration exceeds its source asset's actual `.length`** (floor, don't round)
- [ ] First 2-3 seconds have visual content but no narration (hook breathes)
- [ ] No two consecutive segments use the same visual type
- [ ] All fade transitions are 0.5-1.0 seconds
- [ ] Data call-outs appear after narration mentions them, not before
- [ ] Music track spans full duration at 0.1-0.2 volume (loop if `generate_music()` returned shorter audio)
- [ ] All video/capture assets are muted (volume=0)
- [ ] Narration ends before the outro card appears
- [ ] Outro card is 3-5 seconds, not longer
- [ ] Total duration is within the TARGET_DURATION range from config
- [ ] All `add_clip(start, ...)` start values are integers (whole seconds)
- [ ] All text overlays use font size >= 36px (callouts) or >= 52px (hero stats)
- [ ] No text overlay uses `Position.center` with `Background` (use `Position.bottom` + offset instead, or text-embedded images — see [asset-production.md](asset-production.md) gotcha)
- [ ] Every callout has a semi-opaque background bar (opacity 0.6+) for contrast
- [ ] Callout background bars span at least 30% of frame width (not tiny tooltips)
- [ ] Data callouts are timed 0.5-1s AFTER narration mentions the stat (not before or simultaneous)
