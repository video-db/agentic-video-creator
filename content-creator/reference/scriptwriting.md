# Scriptwriting

Convert a research brief into a video script — a sequence of segments that tells a story with motion, narration, and data.

## Narrative Arc

Every video briefing follows this arc regardless of topic:

```
HOOK (5-10s)     → Grab attention with the most surprising finding
CONTEXT (10-15s) → Why this topic matters, set the stage
INSIGHTS (30-60s)→ 2-3 key findings, each its own segment
TAKEAWAY (10-15s)→ What this means, the "so what"
CLOSE (5s)       → Clean ending, optional CTA
```

The hook is not an intro. Don't open with "today we'll talk about..." — open with the most striking data point, the most unexpected fact, the thing that makes someone stop scrolling.

## Visual Types

Each segment declares a `visual_type` that tells the asset production phase what kind of visual to create. Pick based on what the segment is communicating:

| Visual Type | When to Use | Feels Like |
|-------------|-------------|------------|
| `data_viz` | Showing numbers, trends, comparisons | Animated chart sliding in, counter ticking up |
| `motion_scene` | Setting mood, atmosphere, transitions | AI-generated video clip with motion |
| `browser_capture` | Citing sources, showing evidence | Host navigating real websites on screen |
| `kinetic_text` | Key quotes, stat highlights, punchy moments | Bold text flying onto screen |
| `image_scene` | Abstract concepts where static works | AI image (use sparingly) |

**Visual variety rule:** Never use the same visual type for two consecutive segments. A good sequence might be:

```
hook: motion_scene → context: browser_capture → insight 1: data_viz →
insight 2: kinetic_text → insight 3: browser_capture → takeaway: motion_scene → close: kinetic_text
```

## Script Schema

The script is a JSON object that the agent produces after scriptwriting and passes to the asset production and composition phases.

```json
{
  "title": "Short, punchy title (appears as title card)",
  "segments": [
    {
      "id": "hook",
      "narration": "The spoken narration for this segment. 2-3 sentences, conversational tone. Written to be spoken aloud, not read.",
      "visual_type": "motion_scene",
      "visual_direction": "What the viewer should see. Be specific about motion and content. e.g., 'Aerial drone shot of a bustling tech campus at golden hour, camera slowly pushing forward'",
      "data_callout": null,
      "visual_sync_anchors": [],
      "mood": "surprising, attention-grabbing"
    },
    {
      "id": "context",
      "narration": "According to Gartner's latest report, enterprise AI adoption has crossed a tipping point...",
      "visual_type": "browser_capture",
      "visual_direction": "Navigate to the Gartner report on AI adoption, scroll to the key chart, pause on the headline stat",
      "data_callout": null,
      "visual_sync_anchors": [
        {"word": "Gartner", "expected_visual": "Gartner report page or header visible on screen"}
      ],
      "mood": "grounding, authoritative"
    },
    {
      "id": "insight_1",
      "narration": "The tech sector leads at 73 percent, but healthcare is catching up fast...",
      "visual_type": "data_viz",
      "visual_direction": "Animated bar chart comparing adoption rates across industries, bars growing from left to right, highlight the leader",
      "data_callout": "73% adoption in tech sector",
      "visual_sync_anchors": [
        {"word": "73 percent", "expected_visual": "bar chart visible with tech sector bar highlighted"},
        {"word": "healthcare", "expected_visual": "healthcare bar visible or growing"}
      ],
      "mood": "revealing, analytical"
    }
  ],
  "music_direction": "Modern, minimal electronic. Builds energy through the insights, resolves at takeaway. Think: tech conference background, not epic trailer.",
  "outro": "Brief closing line for the final text card"
}
```

### Field Rules

- **`narration`**: Write for the ear, not the eye. Use contractions. Short sentences. Rhetorical questions work. Never say "in this video" or "let me explain."
- **`visual_type`**: One of `data_viz`, `motion_scene`, `browser_capture`, `kinetic_text`, `image_scene`.
- **`visual_direction`**: Describe motion, not just subject. "Chart bars growing" not "a chart." "Camera pushing forward over a city" not "a city." For `browser_capture`, specify exact URLs or search queries.
- **`data_callout`**: A short stat or phrase overlaid on screen as text. Only when there's a specific number or quote worth highlighting. Null if not needed.
- **`visual_sync_anchors`**: A list of `{"word": "...", "expected_visual": "..."}` pairs. Each anchor identifies a specific word or phrase in the narration and declares what should be visible on screen when the viewer hears it. These are verified during the self-review Narration-Visual Sync pass. Use anchors for: product names, stat mentions, source citations, any moment where the narration explicitly references something the viewer should see. Empty list for abstract segments with no specific entity mentions.
- **`mood`**: Emotional tone. Guides music transitions and visual style.

## Pacing

For a 60-90 second briefing with 4-6 segments:

| Segment | Duration | Purpose |
|---------|----------|---------|
| Hook | 5-10s | Stop the scroll |
| Context | 10-15s | Establish why this matters |
| Insight 1 | 10-15s | First key finding |
| Insight 2 | 10-15s | Second key finding |
| Insight 3 (optional) | 10-15s | Third key finding |
| Takeaway | 10-15s | The "so what" |
| Close | 3-5s | Clean ending |

- The most important insight gets the longest segment.
- Vary segment lengths — short-long-short creates rhythm.
- No segment under 8 seconds (feels rushed) or over 20 seconds (loses attention).

## Audience Adaptation

Adjust based on who's watching:

**Tech audience (SF demo, developer conference):**
- Lead with data, not emotion
- Use precise numbers, not vague claims
- browser_capture of GitHub repos, technical papers, benchmark charts
- Music: minimal, ambient, not distracting

**Business audience (executive briefing):**
- Lead with impact and ROI
- Fewer stats, more "what this means for you"
- browser_capture of market reports, analyst quotes
- Music: confident, professional

**General audience (social, broad):**
- Lead with surprise or emotion
- Analogies and simple language
- More motion_scene and kinetic_text, less browser_capture
- Music: energetic, engaging

## Common Pitfalls

- **Narration-visual mismatch**: Talking about revenue while showing a nature scene. Every visual must relate to what's being said at that moment. Use `visual_sync_anchors` to catch this at script time — if you can't fill in anchors for a segment, the narration and visual are probably misaligned.
- **Narration-visual timing drift**: The narration mentions "Call.md" at t=14 but the browser capture is still loading at t=14 and doesn't show the repo until t=17. Write anchors during scripting, and the self-review sync pass will catch these drifts.
- **Data overload**: More than one data_callout per segment overwhelms the viewer.
- **Monotone pacing**: All segments the same length, same visual type, same energy level. Vary everything.
- **Missing the hook**: Starting with background context instead of the most surprising finding. The hook is not optional.
- **Writing for readers, not listeners**: Narration that sounds like a blog post. Read it aloud — if it feels unnatural, rewrite it.
