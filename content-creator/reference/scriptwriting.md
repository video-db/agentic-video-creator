# Scriptwriting

Convert a research brief into a video script — a sequence of segments that tells a story with motion, narration, and data. **Read the selected format file first** (`reference/formats/*.md`) — it defines persona, pacing, and narrative arc specifics.

## Narrative Arc

The structure depends on the selected format. Read the format file for the full arc definition.

### Briefing Format (60-120s, 4-6 segments)

```
HOOK (5-10s)     → Grab attention with the most surprising finding
CONTEXT (10-15s) → Why this topic matters, set the stage
INSIGHTS (30-60s)→ 2-3 key findings, each its own segment
TAKEAWAY (10-15s)→ What this means, the "so what"
CLOSE (5s)       → Clean ending, optional CTA
```

### Fireship Explainer Format (180-420s, 15-30+ segments)

```
HOOK (3-5s)      → One-liner that stops the scroll. Bold claim, surprising stat, or hot take.
TOPIC 1 (15-30s) → 3-6 rapid segments covering the first point
TOPIC 2 (15-30s) → 3-6 rapid segments covering the second point
...
TOPIC N (15-30s) → 3-6 rapid segments covering the Nth point
TAKEAWAY (5-10s) → "Here's what actually matters"
CTA (3-5s)       → Subscribe, check links, etc.
```

Each topic block alternates between narration-heavy segments and visual punches. Never 2+ consecutive "talking head" segments without a visual interrupt.

The hook is not an intro. Don't open with "today we'll talk about..." — open with the most striking data point, the most unexpected fact, or the most controversial take.

## Visual Types

Each segment declares a `visual_type` that tells the asset production phase what kind of visual to create.

| Visual Type | When to Use | Feels Like |
|-------------|-------------|------------|
| `data_viz` | Showing numbers, trends, comparisons | Animated chart sliding in, counter ticking up |
| `motion_scene` | Setting mood, atmosphere, transitions | AI-generated video clip with motion |
| `browser_capture` | Citing sources, showing evidence | Host navigating real websites on screen |
| `kinetic_text` | Key quotes, stat highlights, punchy moments | Bold text flying onto screen |
| `image_scene` | Abstract concepts where static works | AI image (use sparingly) |
| `code_editor` | Showing code, syntax, config, commands | Animated code editor with typing and highlights |
| `meme_insert` | Humor beats, reaction images, joke moments | Quick meme flash timed to punchline |
| `diagram_animation` | Architecture, flows, concept relationships | Animated diagram building itself |
| `logo_composition` | Tech comparisons, ecosystem overviews | Animated logo grid or flying icons |
| `split_screen` | Before/after, A vs B comparisons | Side-by-side with simultaneous reveals |
| `stock_footage` | Real-world context, physical analogy | Short b-roll clip from stock library |

### Visual Variety Rules

**Briefing format:** Never use the same visual type for two consecutive segments.

**Explainer format:** Same type is OK for back-to-back segments if the content is different (e.g., `code_editor` showing Python then `code_editor` showing JavaScript). But never more than 3 consecutive segments of the same type. Aim for a type change every 2 segments on average.

A good explainer sequence:

```
hook: kinetic_text → topic1_explain: code_editor → topic1_punch: meme_insert →
topic1_evidence: browser_capture → topic2_explain: diagram_animation →
topic2_code: code_editor → topic2_meme: meme_insert → topic3_compare: split_screen →
topic3_evidence: browser_capture → takeaway: kinetic_text → cta: logo_composition
```

## Script Schema

The script is a JSON object produced after scriptwriting and passed to the asset production and composition phases.

```json
{
  "title": "Short, punchy title (appears as title card)",
  "format": "explainer",
  "segments": [
    {
      "id": "hook",
      "narration": "The spoken narration for this segment. 1-3 sentences. Written to be spoken aloud, not read.",
      "visual_type": "kinetic_text",
      "visual_direction": "What the viewer should see. Be specific about motion and content.",
      "data_callout": null,
      "visual_sync_anchors": [],
      "mood": "surprising, attention-grabbing",
      "transition_type": "hard_cut",
      "humor_beat": null,
      "emphasis_words": ["myth", "waste"],
      "code_snippet": null
    },
    {
      "id": "topic1_explain",
      "narration": "A lot of people think you need to know math to be a programmer...",
      "visual_type": "code_editor",
      "visual_direction": "Show a simple Python function — no math involved. Typing animation, highlight the function name.",
      "data_callout": null,
      "visual_sync_anchors": [
        {"word": "math", "expected_visual": "code visible on screen, no math operations"}
      ],
      "mood": "debunking, conversational",
      "transition_type": "hard_cut",
      "humor_beat": null,
      "emphasis_words": ["math", "programmer"],
      "code_snippet": "def greet(name):\n    return f'Hello, {name}!'",
      "overlays": [
        {
          "type": "reaction_clip",
          "direction": "Small AI video of a shrugging developer, cartoon style",
          "position": "bottom_right",
          "scale": 0.18,
          "timing": "start+3s for 2s",
          "opacity": 0.9
        }
      ]
    },
    {
      "id": "topic1_meme",
      "narration": "Unless you're building a physics engine, you'll be fine with basic arithmetic.",
      "visual_type": "meme_insert",
      "visual_direction": "Math lady meme or confused math equations floating in front of a cat",
      "data_callout": null,
      "visual_sync_anchors": [],
      "mood": "comedic relief",
      "transition_type": "hard_cut",
      "humor_beat": "punchline",
      "emphasis_words": ["physics engine"],
      "code_snippet": null
    }
  ],
  "music_direction": "Lo-fi electronic with energy peaks at topic transitions. Subtle bass drops on key reveals. Think: late-night coding session soundtrack.",
  "sfx_direction": "Whoosh on hard cuts, subtle pop on stat reveals, comedic sting on meme beats",
  "outro": "Brief closing line for the final text card"
}
```

### Field Rules

- **`narration`**: Write for the ear, not the eye. Use contractions. Short sentences. Rhetorical questions work. See your format file for persona/voice guidance.
- **`visual_type`**: One of the 11 types listed above.
- **`visual_direction`**: Describe motion, not just subject. "Code typing line by line with cursor" not "some code." "Bar chart bars racing to show winner" not "a chart." For `browser_capture`, specify exact URLs or search queries. For `code_editor`, describe what happens (typing, highlighting, zooming). For `meme_insert`, describe the meme concept or reference a specific template.
- **`data_callout`**: A short stat or phrase overlaid on screen. Only when there's a specific number or quote worth highlighting. Null if not needed.
- **`visual_sync_anchors`**: List of `{"word": "...", "expected_visual": "..."}` pairs. Each anchor identifies a specific word/phrase in narration and declares what should be visible when the viewer hears it. Empty list for abstract segments.
- **`mood`**: Emotional tone. Guides music transitions and visual style.
- **`transition_type`**: How this segment transitions to the next. Options:
  - `hard_cut` — instant switch (default for fireship-explainer)
  - `fade` — 0.5s cross-fade (default for briefing)
  - `whip` — fast horizontal wipe (for energy spikes, topic switches)
  - `graphic` — custom graphic transition (for section breaks)

### Fireship Explainer Extensions (optional fields)

These fields are only used when format = fireship-explainer. Omit them for briefing format.

- **`humor_beat`**: When this segment contains a joke/meme. Options: `setup`, `punchline`, `callback`, or null.
- **`emphasis_words`**: Words in narration that should be visually emphasized (bold flash, zoom, or screen text).
- **`code_snippet`**: If `visual_type` is `code_editor`, include the actual code string here.
- **`transition_type`**: (same as above, but defaults to `hard_cut` for explainer)
- **`sfx_direction`**: Optional SFX hint for composition (e.g., "whoosh", "pop", "comedic sting").
- **`overlays`**: Optional list of small visual elements that play **simultaneously** with the main visual:
  ```json
  {
    "type": "pip_meme | reaction_clip | emphasis_arrow | ambient_loop | logo_badge | stat_counter",
    "direction": "Small confused developer face reacting to the code",
    "position": "bottom_right",
    "scale": 0.2,
    "timing": "start+2s for 3s",
    "opacity": 0.95
  }
  ```
  Use overlays to add visual density without replacing the main content. 3-5 per explainer video.

## Pacing

Pacing rules are defined in the format file. Here's a summary — **read the full format file for details.**

### Briefing Format

- Segments: 8-20 seconds each, sweet spot 12-15s.
- No segment under 8s or over 20s.
- Rhythm: vary lengths, most important insight gets longest segment.

### Fireship Explainer Format

- Segments: 2-10 seconds each, sweet spot 3-5s.
- Rhythm: fast-fast-breathe (two 2-4s segments, one 5-8s).
- Humor beat every 60-90 seconds.
- Maximum 3 sentences per segment — longer = split into two segments.

## Persona

**Personas are defined in the format files.** Read `reference/formats/briefing.md` or `reference/formats/fireship-explainer.md` for full persona details, voice characteristics, and forbidden phrases.

## Audience Adaptation

Adjust based on who's watching:

**Tech audience (SF demo, developer conference):**
- Lead with data, not emotion
- Use precise numbers, not vague claims
- browser_capture of GitHub repos, technical papers, benchmark charts
- code_editor showing real implementations
- Music: minimal, ambient, not distracting

**Business audience (executive briefing):**
- Lead with impact and ROI
- Fewer stats, more "what this means for you"
- browser_capture of market reports, analyst quotes
- data_viz showing business metrics
- Music: confident, professional

**General audience (social, broad):**
- Lead with surprise or emotion
- Analogies and simple language
- More motion_scene, kinetic_text, meme_insert
- Music: energetic, engaging

## Common Pitfalls

- **Narration-visual mismatch**: Talking about revenue while showing a nature scene. Every visual must relate to what's being said at that moment. Use `visual_sync_anchors` to catch this at script time.
- **Narration-visual timing drift**: The narration mentions "React" at t=14 but the code_editor hasn't shown React code until t=17. Write anchors during scripting, and the self-review sync pass will catch these drifts.
- **Data overload**: More than one data_callout per segment overwhelms the viewer.
- **Monotone pacing**: All segments the same length, same visual type, same energy level. Vary everything.
- **Missing the hook**: Starting with background context instead of the most surprising finding.
- **Writing for readers, not listeners**: Narration that sounds like a blog post. Read it aloud.
- **Explainer-specific: too slow**: If a segment narration exceeds 3 sentences in explainer format, split it into two segments. The viewer's attention span for a single shot is 3-5 seconds.
- **Explainer-specific: humor drought**: If you go more than 90 seconds without a humor beat, add a meme_insert or a witty aside.
- **Explainer-specific: monotone visuals**: If you have 3+ code_editor segments in a row without a diagram, meme, or browser break, insert a visual palette cleanser.
