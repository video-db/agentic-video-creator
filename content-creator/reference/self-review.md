# Self-Review

Self-review is **mandatory**. Always run at least one review cycle after the first composition. `MAX_ITERATIONS` (from SKILL.md config) is the maximum number of review-fix cycles — not a toggle. You are a director watching your rough cut. Watch it, critique it, fix it, recut it.

## How to "Watch" the Draft

You can't literally watch video, but you can extract frames, look at them, and read AI descriptions of every second. Use the `videodb` skill to:

### Step 1: Upload the stream

Upload the composed stream URL as a new video asset in VideoDB.

### Step 2: Index spoken words

Transcribes the narration so you can read what was actually said:

```python
video.index_spoken_words()
```

### Step 3: Extract scenes with frames

Extract scenes at 1-second intervals with 2 frames each:

```python
from videodb import SceneExtractionType

scene_collection = video.extract_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 1, "select_frames": ["first", "last"]},
)
```

**Returns:** a `SceneCollection` with a `.scenes` list. Each `Scene` has:
- `.start` — start time in seconds
- `.end` — end time in seconds
- `.description` — text description (empty until you call `.describe()`)
- `.frames` — list of `Frame` objects, each with `.url` and `.frame_time`

### Step 4: Index scenes for AI descriptions

```python
import re

try:
    scene_index_id = video.index_scenes(
        extraction_type=SceneExtractionType.time_based,
        extraction_config={"time": 1, "select_frames": ["first", "last"]},
        prompt="Describe the visual content: what type of visual is this (animated chart, browser/webpage, text on screen, code editor, meme/joke image, diagram, logo grid, split screen, video clip, static image)? What does it show? What text is visible? Is there motion or is it static? Is the code readable?",
    )
except Exception as e:
    match = re.search(r"id\s+([a-f0-9]+)", str(e))
    if match:
        scene_index_id = match.group(1)
    else:
        raise
```

### Step 5: Read back everything

**Transcript (what was said):**

```python
transcript = video.get_transcript()       # list of {start, end, text}
transcript_text = video.get_transcript_text()  # full text string
```

**Scene index records (AI descriptions per second):**

```python
scene_records = video.get_scene_index(scene_index_id)
for record in scene_records:
    print(f"[{record['start']}-{record['end']}] {record['description']}")
```

**Frame images (actually look at what's on screen):**

```python
frames_dir = Path(WORK_DIR) / "frames"
frames_dir.mkdir(parents=True, exist_ok=True)

for scene in scene_collection.scenes:
    print(f"\n--- Scene {scene.start}s - {scene.end}s ---")
    print(f"Description: {scene.description}")
    for frame in scene.frames:
        print(f"  Frame at {frame.frame_time}s: {frame.url}")
```

**Look at the frames.** Don't just read descriptions — download and view frame images using the Read tool. The AI descriptions can miss details. The frame images are ground truth.

**MANDATORY FRAME INSPECTION — CANNOT BE FAKED:** You MUST:
1. Download at least 5 frames from different parts of the video to `{WORK_DIR}/review_frames/`
2. Use the **Read tool** to view each `.png` file (they are image files, the Read tool renders them)
3. For EACH viewed frame, report in your response: what you see, what visual type it is, whether text/code is readable, and whether it matches the intended segment
4. If you report "PASS - readable at 720p" for a code frame **without having actually downloaded and viewed it with Read**, the review is invalid

The purpose of frame inspection is to catch garbled code, cropped memes, missing overlays, and repeated backgrounds that AI scene descriptions will miss.

Download frames like this:
```python
import requests
frames_dir = Path(WORK_DIR) / "review_frames"
frames_dir.mkdir(parents=True, exist_ok=True)

sample_times = [5, 15, 25, 45, 75, 105]  # sample across the video
for scene in scene_collection.scenes:
    for frame in scene.frames[:1]:
        if int(frame.frame_time) in sample_times:
            fpath = frames_dir / f"frame_{frame.frame_time:.0f}s.png"
            resp = requests.get(frame.url)
            fpath.write_bytes(resp.content)
            print(f"Saved: {fpath}")
```

Then use the Read tool to view each `.png` file. If any code_editor frame shows garbled/unreadable characters, that's a FAIL — the code screenshot approach needs to be changed (likely the encoding method is broken).

### Step 6 (optional): Retrieve scenes later

```python
collections = video.list_scene_collection()
scene_collection = video.get_scene_collection(collections[0]["scene_collection_id"])
```

### What you now have

- **What you intended** — the script + the timeline from composition
- **What was said** — transcript from spoken word indexing
- **What the AI sees** — scene descriptions from `get_scene_index()`
- **What actually appears** — frame images you can look at directly

## Build the Intended Timeline

During composition (Phase 4), you placed clips at specific timestamps. Build a lookup:

```
second  0-2:   hook     / kinetic_text     / visual: "Bold text: 7 Myths"
second  2-5:   hook     / kinetic_text     / narration: "Everyone thinks..."
second  5-8:   topic1   / code_editor      / visual: "Python function typing"
second  8-11:  topic1   / meme_insert      / visual: "Confused math lady meme"
...
```

Structure as a list:

```python
intended_timeline = [
    {"start": 0, "end": 2, "segment": "hook", "visual_type": "kinetic_text", "visual_direction": "Bold text...", "narration": None},
    {"start": 2, "end": 5, "segment": "hook", "visual_type": "kinetic_text", "visual_direction": "Bold text...", "narration": "Everyone thinks..."},
    {"start": 5, "end": 8, "segment": "topic1_code", "visual_type": "code_editor", "visual_direction": "Python function typing", "narration": "You don't need math..."},
    # ...
]
```

## Align and Compare

Walk through scene records and frame images, aligning each second against intended timeline:

1. **Look up** what intended timeline says should be at this second
2. **Read** the AI description from `get_scene_index()` for that timestamp
3. **Look at** the frame image — actually view it
4. **Compare**: does both the description AND frame match the intent?

**What to flag:**

| Intended | What you see | Verdict |
|----------|-------------|---------|
| `code_editor` — "Python function" | Dark editor with syntax-highlighted code | Match |
| `code_editor` — "Python function" | White text on dark background, no syntax | Mismatch — wrong rendering |
| `meme_insert` — "confused math meme" | A funny image of confused person with equations | Match |
| `diagram_animation` — "microservices flow" | Boxes with arrows, labels visible | Match |
| `logo_composition` — "React, Vue, Angular logos" | Black screen | Mismatch — rendering failed |

Build a mismatch report:

```python
mismatches = []
for intended in intended_timeline:
    matching_records = [r for r in scene_records if r["start"] >= intended["start"] and r["start"] < intended["end"]]
    for record in matching_records:
        if not visuals_match(intended["visual_direction"], record["description"]):
            mismatches.append({
                "time": f"{record['start']}-{record['end']}",
                "segment": intended["segment"],
                "expected": intended["visual_direction"],
                "actual_description": record["description"],
            })
```

## Critique Framework

Check each of these. Collect all issues before deciding what to fix.

### 0. Production Method Diversity (CHECK FIRST)

**This check runs before anything else.** Count how many segments use each production method.

**Automatic FAIL conditions (all formats):**
- More than 50% of segments used `generate_image` → FAIL. You built a slideshow.
- Any `code_editor` segment used `generate_image` → FAIL. Code will be garbled.
- Fewer than 3 different production methods → FAIL.

**Additional FAIL for fireship-explainer format:**
- No Remotion or Playwright assets → FAIL.
- No real-sourced assets (stock footage, real memes, real logos) → FAIL.
- Sourcing budget violated: AI-generated > 40% of visual segments → FAIL.
- Overlay count < 3 (PiP memes, logo badges, ambient loops, stat counters) → FAIL.
- Any `meme_insert` segment uses a raw uncaptioned template with no TextAsset overlay → FAIL.
- Any non-ambient visual asset ID used for more than one segment → FAIL (background reuse).
- Any TextAsset placed on a Remotion-rendered segment (code_editor, kinetic_text, diagram_animation, data_viz, split_screen) → FAIL (double-text — Remotion videos already contain baked-in text).
- Audio drops/gaps between narration clips → FAIL (narration must chain continuously).

**If this check fails:** Do not proceed with the rest of the review. Go back to Phase 3 and redo asset production. See the "Banned Production Approaches" table in asset-production.md.

**How to check:** Count production methods from Phase 3:
```python
method_counts = {"real_sourced": 0, "generate_image": 0, "generate_video": 0, "remotion": 0, "playwright": 0, "text_asset": 0}
for seg in segments:
    method_counts[seg["production_method"]] += 1
print(method_counts)

total = sum(method_counts.values())
for method, count in method_counts.items():
    if count / total > 0.5:
        print(f"FAIL: {method} used for {count}/{total} segments ({count/total*100:.0f}%)")
```

### 0b. Asset Sourcing Verification (CHECK SECOND)

**Did you actually search before generating?** This verifies the sourcing hierarchy was followed.

**Check:**
- Did you search the asset library collection before each sourcing decision?
- Did you try external APIs (Pexels, Imgflip, GIPHY, Simple Icons) before falling back to `generate_image`/`generate_video`?
- For `meme_insert` segments: are they real meme templates or AI-generated illustrations?
- For `logo_composition` segments: are they real logos from CDNs or AI-generated?
- For `stock_footage`/`motion_scene`/`image_scene`: did you try Pexels/Pixabay first?

**For fireship-explainer format, verify sourcing budget:**

```python
real_sourced = sum(1 for s in segments if s.get("source_type") in ("pexels", "imgflip", "giphy", "simpleicons", "asset_library", "playwright_capture"))
ai_generated = sum(1 for s in segments if s.get("source_type") in ("generate_image", "generate_video"))
rendered = sum(1 for s in segments if s.get("source_type") in ("remotion", "text_asset", "playwright_render"))

total = real_sourced + ai_generated + rendered
print(f"Real-sourced: {real_sourced}/{total} ({real_sourced/total*100:.0f}%)")
print(f"AI-generated: {ai_generated}/{total} ({ai_generated/total*100:.0f}%)")
print(f"Rendered: {rendered}/{total} ({rendered/total*100:.0f}%)")

if ai_generated / total > 0.4:
    print("FAIL: Too many AI-generated assets. Source more real assets.")
```

**CRITICAL: Verify from frames, not just from your plan.** Download at least 2 code_editor frames and visually confirm code is readable. If garbled, production method is BROKEN regardless of intent.

### 1. Narration Accuracy

Compare intended narration with actual transcript.

**Check:**
- Did the voiceover say what you wrote? TTS can mangle numbers, names, or technical terms.
- Are all key facts present?
- Is the pacing natural?

**If broken:** Regenerate voice for the affected segment with adjusted text.

### 2. Visual-Narration Alignment

Use the mismatch report from Align and Compare.

**Check:**
- When narration talks about a concept, is the visual showing relevant content?
- Are data call-outs visible during the right narration moments?
- Is the title card visible at the start?

**If broken:** Regenerate the asset with a clearer prompt, or swap visual type entirely.

### 3. Pacing (format-dependent)

**Read your format file for specific pacing rules.** Universal checks:

- Any segment that exceeds the format's maximum duration? (briefing: 20s, explainer: 10s)
- Any segment under the format's minimum? (briefing: 8s, explainer: 2s)
- Dead air? (Never acceptable in explainer; max 1s in briefing)
- Is the pace consistent throughout?
- Static images held longer than 5 seconds?

### 4. Visual Variety

**Briefing:** Two consecutive segments with same visual type? More than 2 image_scene segments?

**Fireship Explainer:** More than 3 consecutive segments with same visual type? At least 5 different types used? At least one code_editor, one meme_insert, one diagram or logo? No visual type used more than 40% of the time? Are memes real templates (not AI-generated illustrations)?

**If broken:** Swap the visual type of offending segment and regenerate. For memes, re-source using the meme-sourcing recipe.

### 5. Overall Flow

**Check:**
- Does it start strong?
- Does it end cleanly?
- Background music audible but not overpowering?
- Transitions appropriate for format?

### 6. Overlay Design Quality

**Check:**
- Every text overlay rated "bold" or "adequate"?
- No callout below 36px at 720p?
- Hero stats using 52px+ and filling 60%+ of frame?
- Every callout has semi-opaque background bar?
- No `Position.center` + `Background` combo?

### 7. Format-Specific Quality Checks

**Read your format file** for the full list of format-specific self-review criteria. Here's a summary:

**Fireship Explainer format checks:**
- **Sourcing budget:** >50% real-sourced, <30% AI generated? Flag if not.
- **Humor timing:** Do memes land on the punchline? Gap never exceeds 90s?
- **Code readability:** Is code in code_editor segments readable at 720p? Font size adequate? Syntax correct? If produced via `generate_image`, it WILL have errors.
- **Meme relevance:** Does each meme relate to what was just said? Is it a real meme template?
- **Meme captioning:** Does every meme have caption text? Either via Imgflip/Memegen.link API or TextAsset overlay. An uncaptioned raw template is a FAIL.
- **Meme scaling:** Are memes displayed with `Fit.contain`? Cropped memes lose the joke. Download a meme frame and verify full template is visible.
- **Shot variety score:** At least 5 different visual types used.
- **Layering / Overlay count:** At least 3 overlay clips placed (logo badges, PiP reactions, ambient loops, stat counters). Count them from the timeline. Zero overlays = FAIL.
- **Double-text check:** Are any Remotion-rendered segments (code_editor, kinetic_text, diagram_animation, data_viz, split_screen) also covered by a TextAsset overlay? If yes, FAIL — Remotion videos already contain baked-in text. Download a frame from these segments and verify no doubled text layers.
- **Audio continuity:** Listen for narration drops at segment boundaries. Verify narration clips chain continuously with no gaps or overlaps.
- **Background reuse:** Are any two segments using the same visual asset ID? (Ambient loops exempt.) If yes, FAIL.
- **Static image hold time:** Any image on screen > 5 seconds? Flag for splitting.
- **Energy consistency:** Pace never drops below one new visual every 5-7 seconds?
- **SFX placement:** Whooshes on transitions, pops on reveals, stings on memes?
- **Remotion usage:** If `REMOTION_AVAILABLE = True`, was Remotion used for at least one visual (code animation, diagram, data viz)? If available but unused, FAIL.
- **Captions (if requested):** If user asked for captions, were auto-synced captions added (Phase 4.5)? Download 2+ frames and verify captions are visible at bottom-center with `box_highlight` animation active.

**Briefing format checks:**
- **Segment duration:** Any segment under 8s or over 20s?
- **Dead air:** Any gap without narration AND without music?
- **Hook lead:** 2-3s visual before narration?
- **Outro:** Clean fade-out with breathing room?
- **No consecutive same visual type?**

## Critique: Four Passes

### Pass 1: Narration-Visual Sync

Verify what the viewer **hears** matches what they **see** at each second.

**Build anchor moments from the script.** Use `visual_sync_anchors` if provided, otherwise scan word-level transcript for entity mentions.

```python
transcript = video.get_transcript()

anchors = []
for i, word in enumerate(transcript):
    text = word["text"].lower().strip()
    if text in ("react", "python", "typescript", "github", "percentage"):
        anchors.append({
            "time": word["start"],
            "word": word["text"],
            "context": " ".join(t["text"] for t in transcript[max(0,i-2):i+3]),
        })
```

**For each anchor, find the frame at that timestamp and check:**
1. What segment and visual should be playing?
2. Find the extracted frame closest to that time and view it
3. Does the frame show the thing narration is naming?

**Log results in a sync table:**

```
ANCHOR       | TIME   | NARRATION SAYS    | FRAME SHOWS                  | VERDICT
-------------|--------|-------------------|------------------------------|--------
tech_name    | 5.2s   | "React"           | React logo in code editor    | MATCH
stat         | 14.0s  | "73 percent"      | data_viz with 73% bar        | MATCH
meme_ref     | 22.1s  | "everyone says"   | Drake meme image             | MATCH
code_ref     | 31.4s  | "this function"   | black screen, no code        | MISMATCH
```

### Pass 2: Visual inspection (you do this)

Look at frame images yourself. For each segment, find corresponding frames and view them:

```python
for intended in intended_timeline:
    print(f"\n=== {intended['segment']} ({intended['start']}s - {intended['end']}s) ===")
    print(f"Expected: {intended['visual_type']} — {intended['visual_direction']}")
    for scene in scene_collection.scenes:
        for frame in scene.frames:
            if intended["start"] <= frame.frame_time < intended["end"]:
                print(f"  Frame at {frame.frame_time}s: {frame.url}")
```

For each frame ask:
- Does this match what I intended?
- Is the visual type right?
- Is text/code readable?
- Does it look polished or broken?

### Pass 3: Design Taste

Evaluate every text overlay frame as a **graphic designer**. Rate each:

| Rating | Definition | Action |
|--------|-----------|--------|
| **Bold** | Fills screen, impossible to miss, professional | Keep |
| **Adequate** | Readable, decent contrast | Fix if iterations remain |
| **Weak** | Viewer at 1x speed would miss it | **Mandatory fix** |

### Pass 4: LLM critique (automated)

Use `videodb` skill's `generate_text`:

```
You are a video director reviewing a rough cut. Compare intended plan against actual production.

INTENDED TIMELINE:
{intended_timeline data}

ACTUAL TRANSCRIPT:
{transcript with timestamps}

AI SCENE DESCRIPTIONS:
{scene_records from get_scene_index()}

VISUAL INSPECTION NOTES:
{your observations}

FORMAT: {briefing or explainer}

Review as a director. For explainer format, additionally check:
- Humor timing (memes land on punchlines?)
- Code readability (syntax highlighting visible? font readable?)
- Shot variety (enough different visual types?)
- Energy consistency (pace never drops?)
- Information density (every frame teaches or entertains?)

For each issue:
- TIMESTAMP: when it occurs
- SEGMENT: which segment
- PROBLEM: what's wrong
- FIX: specific action
- SEVERITY: critical (must fix) or minor (fix if iterations remain)

If strong and no issues: "PASS".
```

## Director Pass

After the critique, think like a director:

**You have full creative authority to restructure.**

- **Rearrange segments** if flow doesn't work
- **Swap asset types** — code_editor not landing? Try diagram_animation or split_screen
- **Add humor** — pace feeling dry? Insert a meme_insert between heavy segments
- **Adjust pacing** — shorten segments that drag, extend ones that need breathing room
- **Recompose entirely** if the rough cut reveals the segment order doesn't work

## Fix Strategy

| Problem | Fix | Regenerate? |
|---------|-----|-------------|
| Narration mismatch | Adjust text, regenerate voice | Voice only |
| Visual doesn't match narration | Change prompt or visual type | Visual asset |
| Segment too long (explainer) | Split into 2 segments | Voice + visual |
| Consecutive same visual type | Swap one segment's type | One visual asset |
| Music too loud/quiet | Adjust volume | Nothing — recompose |
| Missing data call-out | Add TextAsset | Nothing — recompose |
| Flow/order doesn't work | Rearrange segments | Nothing — recompose |
| Code not readable | Increase font size in Remotion, re-render | Visual asset |
| Meme not funny/relevant | Replace meme image | Visual asset |
| SFX missing or mistimed | Add/move SFX clips | Nothing — recompose |
| Pace drops | Split long segment or remove filler | May need new assets |
| Humor drought (>90s gap) | Insert meme_insert segment | Voice + visual |

## Iteration Rules

- **Mandatory.** Always run at least one review cycle. No exceptions.
- **Max iterations:** Respects `MAX_ITERATIONS` from SKILL.md config (default: 5).
- **When to stop early:** Critique returns "PASS" or only minor issues. Earliest stop: after iteration 1.
- **When to keep going:** Critical issues remain (wrong visuals, dead air, pace drops, unreadable code).
- **Diminishing returns:** Same issue persists after 2 attempts? Accept and move on.

## Delivery

When review passes or iteration limit hit:

1. Print **final stream URL** and **console player URL** (`https://console.videodb.io/player?url={STREAM_URL}`)
   - For public sharing: `https://player.videodb.io/watch?v={STREAM_URL}`
2. Print **segment breakdown** with timestamps:
   ```
   00:00 - 00:03  Hook: kinetic_text — "7 Programming Myths..."
   00:03 - 00:08  Topic 1 Intro: code_editor — "Simple Python function..."
   00:08 - 00:11  Topic 1 Meme: meme_insert — "Math confusion meme"
   ...
   ```
3. Note iterations used and what was fixed
4. If at limit with remaining issues, note what couldn't be resolved
