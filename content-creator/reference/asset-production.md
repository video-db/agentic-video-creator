# Asset Production

For each segment in the script, create a visual asset using the best approach for its `visual_type`. You are the host — you're not just generating pretty pictures, you're producing footage for your show.

## The Five Approaches

### 1. AI-Generated Images

**Use for:** `image_scene` — abstract concepts, mood backgrounds, establishing shots where static is intentional.

Generate an image using the `videodb` skill's `generate_image` capability. Specify `16:9` aspect ratio for landscape, `9:16` for vertical.

**When to pick this:**
- The concept is abstract and hard to film or code-render (e.g., "the future of computing")
- You need a quick atmospheric background behind text overlays
- The segment is short (under 8 seconds) and static won't feel stale

**When NOT to pick this:**
- You have actual data to show (use `data_viz` instead)
- You're citing a real source (use `browser_capture` instead)
- Two or more consecutive segments already use static images

### 2. AI-Generated Video Clips

**Use for:** `motion_scene` — hooks, transitions, atmospheric b-roll with actual motion.

Generate a short video clip using the `videodb` skill's `generate_video` capability. These are 5-8 seconds of AI-generated motion.

**When to pick this:**
- Opening hook — motion grabs attention
- Scene-setting — "the world of X" with atmospheric visuals
- Transitions between major sections
- Emotional beats where mood matters more than data

**Tips:**
- Prompt for camera motion: "drone shot pushing forward", "slow pan across", "camera pulling back to reveal"
- These clips are short (5-8s). If a segment is longer, loop or combine with a text overlay.
- Mute the generated video's audio — your narration and music track replace it.

### 3. Remotion (Code-Rendered Video)

**Use for:** `data_viz` — animated charts, bar graphs, line charts, counters, comparisons, infographics.

Write a Remotion React component that animates the data, render it to a video file, upload to VideoDB, and use it as an asset on the timeline.

**When to pick this:**
- You have specific numbers to visualize (market growth, adoption rates, comparisons)
- You want animated counters ticking up to a number
- You need a side-by-side comparison that builds piece by piece
- The data tells a story that motion makes clearer

**What to build:**
- Bar chart with bars growing to their values
- Line chart with a line drawing itself
- Counter animating from 0 to the target number
- Split-screen comparison with elements appearing one at a time
- Timeline/roadmap with milestones appearing sequentially

**If Remotion is unavailable:** Fall back to kinetic text showing the key numbers with bold styling, or generate an image of the chart as a static fallback.

### 4. Browser Capture (Live Research Footage)

**Use for:** `browser_capture` — citing sources, showing evidence, demonstrating the research process.

Navigate to real web pages (tweets, articles, reports, search results) and capture them as video or screenshots. This creates authentic "journalist showing their work" footage.

**When to pick this:**
- Citing a specific report, article, or dataset
- Showing a Google search to establish that the topic is trending
- Navigating a company's website or product page
- Showing a GitHub repo, documentation, or technical resource
- **Showing real tweets/posts** — navigate to a tweet by a CEO, researcher, or public figure and screenshot or record it. "As Sundar Pichai tweeted last week..." while the actual tweet is on screen.
- **Showing social proof** — LinkedIn posts, Reddit threads, Hacker News comments, Product Hunt launches
- **Showing headlines** — navigate to NYT, TechCrunch, The Verge and show the actual headline
- Any moment where credibility comes from showing the real source

**Two modes** — both use Playwright Python. See [browser-recording.md](browser-recording.md) for the full API patterns.

*Screen recording (dynamic):*
Playwright natively records browser navigation as video via `record_video_dir`. Everything the browser does — navigation, scrolling, page loads — gets captured as a `.webm` file.
1. Write a short Playwright script that opens the URL, scrolls to relevant content, pauses on key sections
2. Playwright saves the recording as a video file on disk
3. Upload the video to VideoDB and use it as a video asset on the timeline

Use this when you want to show the journey — scrolling through search results, navigating between pages, the "live research" effect.

*Screenshot (static but fast):*
Use Playwright's `page.screenshot()` to capture a single frame of a page.
1. Navigate to the exact URL (a specific tweet, article, chart)
2. Take a full-page or element-level screenshot
3. Upload as an image asset — use on the timeline as a still with narration over it

Use this when you just need to flash a single piece of evidence — one tweet, one headline, one chart.

**Tips:**
- Keep browser segments to 10-15 seconds max — screen recordings lose attention fast
- Scroll slowly and deliberately — the viewer needs time to read headlines
- Highlight the key stat or quote by pausing on it for 2-3 seconds
- Your narration should reference what's on screen: "as Sundar Pichai put it...", "this report from McKinsey shows..."
- Works best when the source is visually clean (avoid cluttered pages)
- For tweets: navigate to the individual tweet URL, not the timeline — cleaner framing
- For articles: pause on the headline and subhead, not the full body text

**If Playwright is unavailable:** Fall back to kinetic text quoting the source with attribution: `"AI will transform every industry" — Sundar Pichai, CEO Google`

### 5. Kinetic Text

**Use for:** `kinetic_text` — key quotes, stat highlights, takeaway moments, punchy declarations.

Build text compositions using the `videodb` skill's `TextAsset` with staggered timing, fade transitions, and bold styling. No generation needed — this is pure programmatic composition.

**When to pick this:**
- A powerful stat that deserves to fill the screen: "73% of developers now use AI tools"
- A key quote from the research
- The takeaway moment — the "so what" statement
- Transitions between sections (a single word or phrase as a palate cleanser)

**How to make it feel dynamic:**
- Stagger lines — line 1 appears at t=0, line 2 at t=0.5, line 3 at t=1.0
- Use fade-in transitions on each line
- Large font, bold weight, high contrast (white text on dark background or vice versa)
- Keep text short — max 6-8 words per line, max 3 lines per screen
- Add a subtle background color or gradient to avoid floating text on black

### Design Standards for Text Overlays

These are **hard minimums**, not suggestions. The self-review phase will flag any overlay that falls below these thresholds. All sizes assume 1280x720 resolution — scale proportionally for other resolutions.

**Kinetic text (hero stat / segment star):**
- Font size: 52-72px
- Must fill at least 60% of frame width
- This is the visual centerpiece of the segment — it should dominate the screen
- Use `Position.bottom` with `Offset(y=-0.3)` for center-screen placement (see gotcha below)
- Background: semi-opaque bar at 0.6-0.8 opacity, covering at least 50% of frame width
- If `TextAsset` can't deliver this impact, generate an AI image with the text baked in instead. Prompt: include the exact text as the dominant visual element in the image.

**Data callouts (lower-third style):**
- Font size: 36-48px
- `Position.bottom` with small negative y offset (e.g., `Offset(y=-0.08)`)
- Background bar: semi-opaque black at 0.6-0.75 opacity, at least 40% of frame width
- Must be readable in under 1 second at normal playback speed
- The benchmark: would this look at home as a lower-third on Bloomberg or CNN? If it looks like a tooltip, it's too small.

**Title cards:**
- Font size: 48-60px
- Use `Position.bottom` with `Offset(y=-0.3)` for center-screen, or `Position.bottom` with `Offset(y=-0.08)` for lower-third
- Background bar: 0.6-0.7 opacity, covering 60%+ of frame width
- Should feel like a show title, not a filename

**Subtitle / attribution text:**
- Font size: 24-32px
- Muted color (grey, not white)
- `Position.bottom` with minimal offset
- No background bar needed — this is secondary information

**Known gotcha: `TextAsset` at `Position.center` with `Background` may render invisibly.** This is a confirmed issue in the VideoDB Editor API — center-positioned text with a Background box can produce an invisible or near-invisible result. Always use `Position.bottom` with a negative y `Offset` to simulate center-screen placement, or generate an AI image with the text baked in for any screen-dominating text (hero stats, title cards, close CTAs).

**The quality test:** If the callout doesn't look like it belongs on a Bloomberg terminal, a Netflix documentary title card, or a MKBHD video intro, it's too weak. Regenerate as a text-embedded image if `TextAsset` can't deliver the design quality needed.

## Production Order

1. **Narration audio first.** Generate voiceover for each segment using the `videodb` skill. You need the exact duration of each narration clip to time everything else. **Important:** `voice.length` may return a string — always cast with `float(voice.length)`. Store exact values; use `math.floor(length * 100) / 100` when setting clip durations to avoid exceeding the actual audio length.
2. **Background music second.** Generate one track for the full video duration. **Important:** `generate_music(duration=N)` may return audio significantly shorter than N seconds (e.g., 30s when you asked for 90s). Always check `music.length` after generation. If shorter than the total video, plan to loop the track by placing multiple `AudioAsset` clips at staggered start times on the music track.
3. **Visuals in parallel where possible.** AI images and AI video can be generated concurrently. Remotion renders and browser captures may need sequential execution.

**Critical:** AI-generated videos (`generate_video()`) are 5-8 seconds maximum. If a segment's narration is longer than the generated video (e.g., a 13s hook segment with an 8s video), do **not** set the clip duration beyond the video's actual length — this will raise `InvalidRequestError`. Instead, start the next segment's visual asset early to fill the visual gap, or generate a supplementary image to cover the remaining time.

## Mixing Approaches

A well-produced briefing uses 3-4 different approaches across its segments. Here are example mixes:

**Data-heavy topic (market analysis, tech trends):**
```
hook: motion_scene → context: browser_capture → insight 1: data_viz →
insight 2: kinetic_text → takeaway: data_viz → close: kinetic_text
```

**Narrative topic (company story, event recap):**
```
hook: motion_scene → context: browser_capture → insight 1: browser_capture →
insight 2: motion_scene → takeaway: kinetic_text → close: kinetic_text
```

**Abstract topic (philosophy, future predictions):**
```
hook: kinetic_text → context: motion_scene → insight 1: data_viz →
insight 2: motion_scene → takeaway: kinetic_text → close: image_scene
```
