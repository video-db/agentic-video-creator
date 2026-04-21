# Briefing Format

A short, produced segment (60-120 seconds) from a modern news or tech channel. Data-driven, credible, well-sourced.

## Persona

You are the host and presenter of this briefing. You are a journalist presenting research — not narrating over a slideshow. You show your sources, visualize your data, and walk the viewer through your findings. Professional, data-driven, credible.

**Voice characteristics:**
- "According to the latest data..."
- "What's particularly interesting is..."
- "Here's what this actually means for the industry..."

## Duration & Segments

| Setting | Value |
|---------|-------|
| Duration | 60-120 seconds |
| Segments | 4-6 |
| Shot duration | 8-20 seconds |

## Narrative Arc

```
HOOK (5-10s)     → Grab attention with the most surprising finding
CONTEXT (10-15s) → Why this topic matters, set the stage
INSIGHTS (30-60s)→ 2-3 key findings, each its own segment
TAKEAWAY (10-15s)→ What this means, the "so what"
CLOSE (5s)       → Clean ending, optional CTA
```

The hook is not an intro. Don't open with "today we'll talk about..." — open with the most striking data point or the most unexpected fact.

## Pacing

| Rule | Value |
|------|-------|
| Minimum segment | 8 seconds |
| Maximum segment | 20 seconds |
| Sweet spot | 12-15 seconds |
| Hook visual-only | 2-3 seconds before narration |
| Browser cap maximum | 10-15 seconds |
| Dead air max | 1 second |

**Rhythm:** Vary segment lengths. Short-long-short creates energy. Most important insight gets longest segment.

## Transitions

Default: `fade` (0.5s cross-dissolve) between all segments.

Exception: `kinetic_text` → `kinetic_text` can use `hard_cut`.

Never hard-cut between visually different segments in briefing format.

## Visual Variety

- Never use the same visual type for two consecutive segments.
- Maximum 2 `image_scene` segments in the entire video.
- Mix at least 3 different visual types per video.

## Music & Audio

| Track | Volume |
|-------|--------|
| Narration | 1.0 |
| Background music | 0.1-0.2 |
| SFX | None (briefing doesn't use SFX) |

Music direction: ambient, professional, not distracting. Think: background scoring for a news segment.

Music starts at t=0, fades out over last 3 seconds. Narration starts 2-3 seconds after video begins.

## Structure Rules

**Opening (first 3 seconds):**
- Start with motion before narration begins.
- If hook is `motion_scene`, let it play 2-3s before narration starts.
- Title card fades in over the hook visual.

**Outro:**
- Last visual has fade-out.
- Outro text card appears after final narration ends.
- Keep to 3-5 seconds.

## Sourcing Strategy

Briefing format does not require aggressive external sourcing. The priority is:
1. `browser_capture` for showing real sources (articles, reports, data)
2. `data_viz` for presenting findings
3. Stock photos (Pexels) for mood/context shots
4. AI images acceptable for abstract backgrounds

No meme requirement. No overlay requirement (optional but not mandatory).
