# GIF Reactions Sourcing

Short animated clips for PiP overlays and full-frame reaction beats. Real reaction GIFs have more impact than AI-generated "cartoon character shrugging" — the audience recognizes them instantly.

## When to Use

| Situation | Usage pattern |
|---|---|
| Punchline during a code segment | PiP overlay (bottom-right, 2-3s) |
| Full-frame humor beat | Main visual (2-3s, hard cut in/out) |
| Reaction to a surprising fact | PiP overlay during explanation |
| Celebration moment | Full-frame or PiP |
| Confusion/WTF moment | PiP during complex explanation |

## GIPHY API (Primary)

Free beta tier: 100 requests/hour. Returns GIFs with direct MP4 download URLs.

**Env var:** `GIPHY_API_KEY`

### Search for Reaction GIFs

```python
import os
import requests
from pathlib import Path

GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

def search_reaction_gifs(query: str, limit: int = 5) -> list:
    """Search GIPHY for reaction GIFs. Returns MP4 URLs for video use."""
    if not GIPHY_API_KEY:
        return []
    resp = requests.get(
        "https://api.giphy.com/v1/gifs/search",
        params={
            "api_key": GIPHY_API_KEY,
            "q": query,
            "limit": limit,
            "rating": "pg",
            "lang": "en",
        },
    )
    if resp.status_code != 200:
        return []
    
    results = []
    for gif in resp.json().get("data", []):
        images = gif.get("images", {})
        # Prefer original MP4 for quality
        mp4_url = images.get("original", {}).get("mp4")
        if not mp4_url:
            mp4_url = images.get("fixed_height", {}).get("mp4")
        if mp4_url:
            results.append({
                "url": mp4_url,
                "title": gif.get("title", ""),
                "id": gif["id"],
                "width": int(images.get("original", {}).get("width", 480)),
                "height": int(images.get("original", {}).get("height", 360)),
            })
    return results
```

### Download and Upload

```python
def download_gif_as_video(gif: dict, work_dir: str, asset_coll) -> object:
    """Download GIF as MP4 and upload to asset collection."""
    local_path = f"{work_dir}/sourced/gif_{gif['id']}.mp4"
    Path(f"{work_dir}/sourced").mkdir(parents=True, exist_ok=True)
    
    resp = requests.get(gif["url"])
    with open(local_path, "wb") as f:
        f.write(resp.content)
    
    name = f"giphy_{gif['title'][:30].replace(' ', '_')}_{gif['id']}"
    uploaded = asset_coll.upload(file_path=local_path, name=name)
    
    # Index for future semantic search
    uploaded.index_scenes(
        extraction_type=SceneExtractionType.time_based,
        extraction_config={"time": 1, "select_frames": ["first"]},
        prompt="Describe this reaction GIF: emotion, character, action, context.",
    )
    return uploaded
```

## Usage Patterns

### Full-Frame Reaction (Main Visual)

Use when the meme/reaction IS the segment's primary content (humor beat):

```python
gif_asset = download_gif_as_video(gifs[0], WORK_DIR, asset_coll)

visual_track.add_clip(seg_start, Clip(
    asset=VideoAsset(id=gif_asset.id, volume=0),
    duration=min(3, math.floor(float(gif_asset.length) * 100) / 100),
    fit=Fit.crop,
))

# Pair with comedic sting SFX
sfx_track.add_clip(seg_start, Clip(
    asset=AudioAsset(id=comedy_sting.id, volume=0.6),
    duration=min(1.0, float(comedy_sting.length)),
))
```

### PiP Overlay (Corner Reaction)

Use when you want humor without cutting away from the main visual:

```python
gif_asset = download_gif_as_video(gifs[0], WORK_DIR, asset_coll)

overlay_track.add_clip(seg_start + 2, Clip(
    asset=VideoAsset(id=gif_asset.id, volume=0),
    duration=min(3, math.floor(float(gif_asset.length) * 100) / 100),
    scale=0.20,
    position=Position.bottom_right,
    offset=Offset(x=-0.05, y=-0.05),
    opacity=0.95,
))
```

## Query Strategies

Pick queries that match the emotional beat of the narration:

| Emotional context | GIPHY queries to try |
|---|---|
| Bad code / tech debt | "facepalm", "cringe", "disappointed", "this is fine" |
| It works! / Success | "celebration", "success dance", "applause", "victory" |
| Confusion / complexity | "confused", "thinking hard", "head scratch", "wat" |
| Surprise / mind blown | "shocked", "mind blown", "surprised", "jaw drop" |
| Frustration / debugging | "angry typing", "frustrated", "rage quit", "flip table" |
| Agreement / validation | "nodding yes", "exactly", "thank you", "preach" |
| Disagreement / hot take | "no way", "disagree", "shake head", "nope" |
| Speed / performance | "fast", "speed", "zoom", "lightning" |
| Waiting / slow builds | "waiting", "bored", "checking watch", "skeleton waiting" |

**Tips for better results:**
- Add "developer" or "coding" to queries for tech-relevant results
- Add "reaction" to get classic reaction GIF formats
- Keep queries to 2-3 words for best results
- Review titles in results to pick the most relevant one

## Fallback: AI-Generated Reaction Video

If GIPHY API key is not available or returns no results:

```python
reaction_vid = coll.generate_video(
    prompt="Small cartoon character doing a facepalm, simple animation, clean background, reaction GIF style",
)
```

This is acceptable but less impactful than real reaction GIFs that audiences recognize.

## Limits and Guidelines

- **Duration:** GIFs are typically 1-4 seconds. Never extend beyond actual `.length`.
- **Volume:** Always `volume=0`. GIFs are silent.
- **Scale for PiP:** 0.18-0.25 (noticeable but not competing with main content).
- **Frequency:** 1-2 reaction overlays per minute maximum. They're spice.
- **Relevance:** The reaction must match the emotional context of the narration at that moment.
- **Rating:** Always use `rating=pg` in GIPHY queries. No NSFW content.
