# Research Phase

Turn any topic into a structured research brief by launching parallel subagents that investigate different angles simultaneously.

## Decompose the Topic

Before launching subagents, break the topic into 3-5 independent research angles. Each angle should be investigable on its own without needing results from other angles.

**Example:** Topic = "The rise of AI coding assistants"

| Angle | What to investigate |
|-------|-------------------|
| Market landscape | Key players, market size, growth rate, funding |
| Technical capabilities | What they can do today, benchmarks, limitations |
| Developer adoption | Usage stats, sentiment, workflow changes |
| Business impact | Productivity gains, cost savings, case studies |
| Future trajectory | Upcoming capabilities, risks, industry predictions |

**Decomposition prompt (use internally):**

```
Given the research topic: "{topic}"

Break this into 3-5 independent research angles. Each angle should:
- Be investigable independently (no dependencies between angles)
- Cover a distinct aspect of the topic
- Yield concrete facts, stats, or insights (not just opinions)
- Be specific enough for a focused 5-minute investigation

Return a list of angles, each with:
- angle_name: short label
- investigation_focus: what specifically to look for
- example_questions: 2-3 concrete questions to answer
```

## Launch Parallel Subagents

Use the `Task` tool to launch one subagent per research angle. **Launch all subagents in a single message** so they run in parallel.

Each subagent should be:
- `subagent_type="generalPurpose"` for topics needing web search and reasoning
- `subagent_type="explore"` for topics where codebase or local context is relevant
- `model="fast"` is usually sufficient for research gathering

**Subagent prompt template:**

```
Research the following angle about "{topic}":

Angle: {angle_name}
Focus: {investigation_focus}

Instructions:
1. Search the web for current, reliable information
2. Find 3-5 key facts, statistics, or insights
3. Note the source for each finding
4. Flag anything surprising or counterintuitive
5. Note any data that would make a compelling visual (charts, comparisons, timelines)

Return your findings as:
- KEY FACTS: numbered list of findings with sources
- VISUAL OPPORTUNITIES: data points that could be visualized (charts, comparisons)
- STANDOUT INSIGHT: the single most interesting or surprising finding
- CONFIDENCE: how confident you are in these findings (high/medium/low)
```

## Merge Results

After all subagents return, merge their findings into a single research brief. This brief is what the scriptwriting phase consumes.

**Merge strategy:**
1. Collect all KEY FACTS across angles
2. Deduplicate — if two angles found the same stat, keep the one with the better source
3. Flag contradictions — if angles disagree on a fact, note both versions and sources
4. Rank by impact — which facts will resonate most with the target audience?
5. Collect all VISUAL OPPORTUNITIES — these feed directly into the script's visual types
6. Select the top STANDOUT INSIGHT — this becomes the video's hook

**Research brief output format:**

```
TOPIC: {topic}
HOOK: {the single most compelling finding — opens the video}

FINDINGS (ranked by impact):
1. {fact} — Source: {source} — Visual potential: {yes/no, what kind}
2. {fact} — Source: {source} — Visual potential: {yes/no, what kind}
...

CONTRADICTIONS (if any):
- {fact A says X, fact B says Y} — {which seems more reliable and why}

VISUAL OPPORTUNITIES:
- {data point suitable for animated chart}
- {comparison suitable for side-by-side}
- {source article worth showing on screen via browser capture}
...

NARRATIVE THREAD:
{2-3 sentences describing the story these facts tell when sequenced together}
```

## Tips

- **More angles is not always better.** 3 focused angles beat 5 shallow ones. Each subagent should go deep, not wide.
- **Recency matters.** Prompt subagents to prioritize recent data (last 12 months) unless the topic is historical.
- **Visual opportunities are gold.** The scriptwriting phase will use these to decide visual types. A research brief with no visual opportunities produces a boring video.
- **The hook decides everything.** Spend time picking the right standout insight — it's the first thing the viewer hears and sees.
