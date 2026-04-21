# Stock Footage Sourcing

Real video clips and photos from stock APIs. These replace AI-generated visuals for `stock_footage`, `motion_scene`, and `image_scene` segments with authentic, professional-quality footage.

## When to Use

| Visual Type | What to search for |
|---|---|
| `stock_footage` | Direct from script's `visual_direction` |
| `motion_scene` | Cinematic/atmospheric clips (aerial, nature, tech) |
| `image_scene` | Background photos, mood shots, abstract textures |

## Priority Chain

```
1. Search asset library (asset-library.md)
2. Pexels API (primary — free, high quality, landscape-oriented)
3. Pixabay API (fallback — free, alternative catalog)
4. generate_video / generate_image (last resort)
```

## Pexels API (Primary)

Free tier: 200 requests/hour. No watermarks. HD/4K available. Landscape orientation preferred.

**Env var:** `PEXELS_API_KEY` (optional — if missing, skip Pexels and try Pixabay or generate)

### Search Videos

```python
import os
import requests

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def search_pexels_videos(query: str, per_page: int = 5) -> list:
    """Search Pexels for HD landscape video clips."""
    if not PEXELS_API_KEY:
        return []
    resp = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "per_page": per_page, "orientation": "landscape"},
    )
    if resp.status_code != 200:
        return []
    videos = resp.json().get("videos", [])
    results = []
    for v in videos:
        for f in v.get("video_files", []):
            if f.get("quality") == "hd" and f.get("width", 0) >= 1280:
                results.append({
                    "url": f["link"],
                    "duration": v["duration"],
                    "id": v["id"],
                    "width": f.get("width"),
                    "height": f.get("height"),
                })
                break
    return results
```

### Search Photos

```python
def search_pexels_photos(query: str, per_page: int = 5) -> list:
    """Search Pexels for high-resolution landscape photos."""
    if not PEXELS_API_KEY:
        return []
    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "per_page": per_page, "orientation": "landscape"},
    )
    if resp.status_code != 200:
        return []
    return [
        {"url": p["src"]["large2x"], "id": p["id"], "alt": p.get("alt", "")}
        for p in resp.json().get("photos", [])
    ]
```

### Download and Upload

```python
def download_and_upload_video(url: str, name: str, asset_coll, work_dir: str) -> object:
    """Download a video from URL, upload to asset collection."""
    local_path = f"{work_dir}/sourced/{name}.mp4"
    Path(f"{work_dir}/sourced").mkdir(parents=True, exist_ok=True)
    
    resp = requests.get(url, stream=True)
    with open(local_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    
    uploaded = asset_coll.upload(file_path=local_path, name=name)
    return uploaded

def download_and_upload_photo(url: str, name: str, asset_coll, work_dir: str) -> object:
    """Download a photo from URL, upload to asset collection."""
    local_path = f"{work_dir}/sourced/{name}.jpg"
    Path(f"{work_dir}/sourced").mkdir(parents=True, exist_ok=True)
    
    resp = requests.get(url)
    with open(local_path, "wb") as f:
        f.write(resp.content)
    
    uploaded = asset_coll.upload(file_path=local_path, name=name)
    return uploaded
```

## Pixabay API (Fallback)

Free tier: 100 requests/60 seconds. Lower quality than Pexels but broader catalog.

**Env var:** `PIXABAY_API_KEY`

### Search Videos

```python
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def search_pixabay_videos(query: str, per_page: int = 5) -> list:
    """Search Pixabay for video clips."""
    if not PIXABAY_API_KEY:
        return []
    resp = requests.get(
        "https://pixabay.com/api/videos/",
        params={"key": PIXABAY_API_KEY, "q": query, "per_page": per_page},
    )
    if resp.status_code != 200:
        return []
    hits = resp.json().get("hits", [])
    results = []
    for h in hits:
        large = h.get("videos", {}).get("large", {})
        if large.get("url"):
            results.append({
                "url": large["url"],
                "duration": h.get("duration"),
                "id": h["id"],
                "width": large.get("width"),
                "height": large.get("height"),
            })
    return results
```

### Search Photos

```python
def search_pixabay_photos(query: str, per_page: int = 5) -> list:
    """Search Pixabay for photos."""
    if not PIXABAY_API_KEY:
        return []
    resp = requests.get(
        "https://pixabay.com/api/",
        params={"key": PIXABAY_API_KEY, "q": query, "per_page": per_page, "orientation": "horizontal"},
    )
    if resp.status_code != 200:
        return []
    return [
        {"url": h["largeImageURL"], "id": h["id"], "tags": h.get("tags", "")}
        for h in resp.json().get("hits", [])
    ]
```

## Query Patterns Per Visual Type

| Visual Type | Query strategy | Example queries |
|---|---|---|
| `stock_footage` | Direct from `visual_direction` | "developer typing at desk", "server room blue lights" |
| `motion_scene` | Cinematic + mood keywords | "aerial city night neon", "abstract particles dark", "ocean waves slow motion" |
| `image_scene` | Abstract/mood + color direction | "dark technology gradient", "minimalist workspace", "code on screen dark" |

**Tips for better results:**
- Add "dark" or "dark background" for tech videos (matches the dark UI aesthetic)
- Add "aerial" or "drone" for establishing shots
- Use "abstract" + the concept for mood backgrounds
- Be specific: "python code on monitor" > "programming"

## Clip Selection Rules

- Prefer clips 3-8 seconds (matches segment durations)
- Always use landscape orientation
- Mute all stock footage (`volume=0`)
- Prefer clips with camera movement over static shots
- HD minimum (1280x720), prefer Full HD (1920x1080)

## After Sourcing

Always upload to the asset collection for future reuse:

```python
uploaded = download_and_upload_video(
    url=results[0]["url"],
    name=f"pexels_{query.replace(' ', '_')[:30]}_{results[0]['id']}",
    asset_coll=asset_coll,
    work_dir=WORK_DIR,
)
# Index for future semantic search
uploaded.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 2, "select_frames": ["first"]},
    prompt="Describe: subject, action, setting, mood, colors.",
)
```
