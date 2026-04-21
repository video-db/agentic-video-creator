# Meme Sourcing

Source real meme templates and reaction images instead of AI-generating cartoon illustrations. Real memes land better with developer audiences because they recognize the format.

## Priority Chain

```
1. Search asset library (asset-library.md)
2. Imgflip API (top 100 templates, free, no auth for listing)
3. Memegen.link (URL-based generation, free, open source)
4. GIPHY (animated meme GIFs as MP4, free beta)
5. Know Your Meme via Playwright (browse for specific templates)
6. generate_image (last resort — custom humor that doesn't map to any template)
```

## 1. Imgflip API (Primary)

Free. No auth needed for `GET /get_memes`. Returns the top ~100 most popular meme templates with names, URLs, dimensions.

### Get Available Templates

```python
import requests

def get_popular_memes() -> list:
    """Returns top ~100 meme templates from Imgflip."""
    resp = requests.get("https://api.imgflip.com/get_memes")
    if resp.status_code == 200 and resp.json().get("success"):
        return resp.json()["data"]["memes"]  # [{id, name, url, width, height, box_count}]
    return []
```

### Template Selection (LLM picks)

After fetching templates, present the name list to yourself and pick the best match for the narration context:

```python
memes = get_popular_memes()
meme_names = [f"{m['id']}: {m['name']}" for m in memes]

# You (the LLM) review this list and pick the best template
# based on the segment's narration and humor_beat context.
# Example: narration about "choosing between two options" → "Two Buttons" or "Drake Hotline Bling"
```

Common templates and when to use them:
- **Drake Hotline Bling** → rejecting one thing, preferring another
- **Distracted Boyfriend** → tempted by new thing, ignoring current
- **This Is Fine** → situation is clearly bad but pretending it's OK
- **Change My Mind** → strong opinion stated confidently
- **Expanding Brain** → escalating levels of something (ironic)
- **One Does Not Simply** → something that's harder than it looks
- **Surprised Pikachu** → obvious consequence that "surprises" someone
- **Is This a Pigeon?** → misidentifying something obvious

### Download Template

```python
def download_meme_template(meme: dict, work_dir: str) -> str:
    """Download meme template image."""
    local_path = f"{work_dir}/sourced/meme_{meme['id']}.jpg"
    Path(f"{work_dir}/sourced").mkdir(parents=True, exist_ok=True)
    resp = requests.get(meme["url"])
    with open(local_path, "wb") as f:
        f.write(resp.content)
    return local_path
```

### Optional: Caption the Meme (requires free account)

```python
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")

def caption_meme(template_id: str, top_text: str, bottom_text: str) -> str:
    """Generate captioned meme via Imgflip. Returns image URL."""
    if not IMGFLIP_USERNAME or not IMGFLIP_PASSWORD:
        return None
    resp = requests.post("https://api.imgflip.com/caption_image", data={
        "template_id": template_id,
        "username": IMGFLIP_USERNAME,
        "password": IMGFLIP_PASSWORD,
        "text0": top_text,
        "text1": bottom_text,
    })
    if resp.status_code == 200 and resp.json().get("success"):
        return resp.json()["data"]["url"]
    return None
```

If captioning is available, download the captioned image and upload to asset collection.

**If Imgflip credentials are NOT set (no captioning API):** You MUST still add captions using a `TextAsset` overlay on the timeline during composition. A bare template without context-specific text is weak — the audience needs the joke text to land. See the "Meme Caption Overlay" section in meme-humor.md.

### Captioning via Memegen.link (free, no auth fallback)

If Imgflip captioning isn't available, use Memegen.link to produce a pre-captioned image:

```python
def caption_meme_memegen(template_id: str, top: str, bottom: str, work_dir: str) -> str:
    """Generate captioned meme via Memegen.link. Free, no auth."""
    top_clean = top.replace(" ", "_").replace("?", "~q").replace("#", "~h").replace("/", "~s")
    bottom_clean = bottom.replace(" ", "_").replace("?", "~q").replace("#", "~h").replace("/", "~s")
    url = f"https://api.memegen.link/images/{template_id}/{top_clean}/{bottom_clean}.png"
    resp = requests.get(url)
    if resp.status_code == 200:
        local_path = f"{work_dir}/sourced/memegen_{template_id}.png"
        Path(f"{work_dir}/sourced").mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(resp.content)
        return local_path
    return None
```

**Priority: Imgflip caption API → Memegen.link caption → raw Imgflip template + TextAsset overlay.**

## 2. Memegen.link (Fallback)

Free, open-source, no auth. URL-based meme generation — construct the URL and download.

### Get Templates

```python
def get_memegen_templates() -> list:
    """Get all available Memegen.link templates."""
    resp = requests.get("https://api.memegen.link/templates/")
    if resp.status_code == 200:
        return resp.json()  # [{id, name, lines, example, ...}]
    return []
```

### Generate by URL

```python
def get_memegen_url(template_id: str, top: str, bottom: str) -> str:
    """Construct Memegen.link image URL with captions."""
    # Replace spaces with underscores, special chars with ~
    top_clean = top.replace(" ", "_").replace("?", "~q").replace("#", "~h")
    bottom_clean = bottom.replace(" ", "_").replace("?", "~q").replace("#", "~h")
    return f"https://api.memegen.link/images/{template_id}/{top_clean}/{bottom_clean}.png"
```

Note: Memegen.link has a small watermark on free tier. Acceptable for fast-cut 2-3 second meme flashes.

## 3. GIPHY (Animated Memes)

For memes that need MOTION — reaction GIFs are more impactful than static images for some humor beats.

**Env var:** `GIPHY_API_KEY` (free beta key available at developers.giphy.com)

```python
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

def search_giphy_memes(query: str, limit: int = 5) -> list:
    """Search GIPHY for animated meme GIFs (returns MP4 URLs)."""
    if not GIPHY_API_KEY:
        return []
    resp = requests.get(
        "https://api.giphy.com/v1/gifs/search",
        params={"api_key": GIPHY_API_KEY, "q": query, "limit": limit, "rating": "pg"},
    )
    if resp.status_code != 200:
        return []
    results = []
    for gif in resp.json().get("data", []):
        mp4_url = gif.get("images", {}).get("original", {}).get("mp4")
        if mp4_url:
            results.append({
                "url": mp4_url,
                "title": gif.get("title", ""),
                "id": gif["id"],
            })
    return results
```

Download the MP4, upload to VideoDB as a video asset. Use as full-frame meme clip (2-3s) or PiP overlay.

## 4. Know Your Meme via Playwright (Specific Templates)

For finding specific classic memes that aren't in Imgflip's top 100. Browse with Playwright automation.

```python
from playwright.sync_api import sync_playwright

def search_know_your_meme(query: str, work_dir: str) -> str:
    """Browse Know Your Meme, find and screenshot a meme template."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(f"https://knowyourmeme.com/search?q={query}")
        page.wait_for_load_state("networkidle")
        
        # Find first result link
        first_result = page.query_selector(".entry-grid-body a")
        if first_result:
            first_result.click()
            page.wait_for_load_state("networkidle")
            
            # Find the main image
            img = page.query_selector(".photo img, .entry-body img")
            if img:
                img_url = img.get_attribute("src")
                if img_url:
                    # Download the image
                    local_path = f"{work_dir}/sourced/kym_{query.replace(' ', '_')[:20]}.jpg"
                    resp = requests.get(img_url)
                    with open(local_path, "wb") as f:
                        f.write(resp.content)
                    browser.close()
                    return local_path
        
        browser.close()
        return None
```

## 5. AI generate_image (Last Resort)

Only use when:
- The humor concept is too custom/unique to map to any existing template
- All external APIs failed or keys are missing
- The joke requires a specific scene that doesn't exist as a meme format

When using AI generation, follow the prompt engineering from meme-humor.md:
```
[Character/subject] [doing what] [in what context], [art style], [mood/emotion]
```

## Upload to Asset Collection

After sourcing from ANY external source, upload to the collection:

```python
uploaded = asset_coll.upload(file_path=local_path, name=f"meme_{description[:40]}")
```

For GIPHY MP4s (video memes):
```python
uploaded = asset_coll.upload(file_path=local_mp4_path, name=f"giphy_meme_{query[:30]}")
# Index for future search
uploaded.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 1, "select_frames": ["first"]},
    prompt="Describe this meme/reaction: what emotion, what format, what's funny about it.",
)
```

## Meme Selection Heuristics

| Narration context | Good meme choice | Source |
|---|---|---|
| "Two options, one is clearly better" | Drake Hotline Bling | Imgflip |
| "Something that seems easy but isn't" | One Does Not Simply | Imgflip |
| "Situation is bad, pretending it's fine" | This Is Fine | Imgflip |
| "Obvious consequence that surprises people" | Surprised Pikachu | Imgflip |
| "Developer frustration" | "facepalm developer" reaction GIF | GIPHY |
| "Celebration / it works" | "celebration success" GIF | GIPHY |
| "Confusion / WTF moment" | "confused math lady" | Imgflip or KYM |
| "Mind blown by a fact" | "mind blown" reaction GIF | GIPHY |
