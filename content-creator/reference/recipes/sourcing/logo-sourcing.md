# Logo Sourcing

Real tech logos for `logo_composition` segments and logo badge overlays. Always use real SVG/PNG logos from CDNs — never AI-generate logos (they'll be wrong).

## Priority Chain

```
1. Simple Icons CDN (primary — 3400+ brands, free, no auth)
2. devicon CDN (fallback — 150+ dev tools)
3. geticon.dev (fallback — company favicons/logos)
4. Playwright screenshot (last resort — screenshot from official site)
```

## 1. Simple Icons CDN (Primary)

3400+ brand/tech SVG logos. Free, no auth, no rate limits.

### URL Pattern

```python
def get_simple_icon_url(name: str, color: str = None) -> str:
    """Get SVG logo URL from Simple Icons CDN.
    
    Slug rules: lowercase, no spaces, + → plus, . → dot, # → sharp
    """
    slug = (name.lower()
            .replace(" ", "")
            .replace("+", "plus")
            .replace(".", "dot")
            .replace("#", "sharp"))
    
    if color:
        return f"https://cdn.simpleicons.org/{slug}/{color}"
    return f"https://cdn.simpleicons.org/{slug}"
```

### Common Slugs

| Technology | Slug | URL |
|---|---|---|
| Python | `python` | `https://cdn.simpleicons.org/python` |
| JavaScript | `javascript` | `https://cdn.simpleicons.org/javascript` |
| TypeScript | `typescript` | `https://cdn.simpleicons.org/typescript` |
| React | `react` | `https://cdn.simpleicons.org/react` |
| Vue.js | `vuedotjs` | `https://cdn.simpleicons.org/vuedotjs` |
| Angular | `angular` | `https://cdn.simpleicons.org/angular` |
| Node.js | `nodedotjs` | `https://cdn.simpleicons.org/nodedotjs` |
| Docker | `docker` | `https://cdn.simpleicons.org/docker` |
| Kubernetes | `kubernetes` | `https://cdn.simpleicons.org/kubernetes` |
| PostgreSQL | `postgresql` | `https://cdn.simpleicons.org/postgresql` |
| MongoDB | `mongodb` | `https://cdn.simpleicons.org/mongodb` |
| Redis | `redis` | `https://cdn.simpleicons.org/redis` |
| AWS | `amazonaws` | `https://cdn.simpleicons.org/amazonaws` |
| Go | `go` | `https://cdn.simpleicons.org/go` |
| Rust | `rust` | `https://cdn.simpleicons.org/rust` |
| Svelte | `svelte` | `https://cdn.simpleicons.org/svelte` |
| Next.js | `nextdotjs` | `https://cdn.simpleicons.org/nextdotjs` |
| GitHub | `github` | `https://cdn.simpleicons.org/github` |
| Linux | `linux` | `https://cdn.simpleicons.org/linux` |
| C++ | `cplusplus` | `https://cdn.simpleicons.org/cplusplus` |

### Download SVG and Convert to PNG

SVGs need to be rendered to PNG for VideoDB (which works with raster images). Use Playwright:

```python
from playwright.sync_api import sync_playwright

def download_logo_as_png(name: str, work_dir: str, size: int = 256, color: str = None) -> str:
    """Download SVG logo from Simple Icons and render to PNG."""
    url = get_simple_icon_url(name, color)
    local_path = f"{work_dir}/sourced/logo_{name.lower().replace(' ', '_')}.png"
    Path(f"{work_dir}/sourced").mkdir(parents=True, exist_ok=True)
    
    # Render SVG to PNG using Playwright
    html = f"""<!DOCTYPE html>
<html><head><style>
body {{ margin:0; display:flex; align-items:center; justify-content:center;
       width:{size}px; height:{size}px; background:transparent; }}
img {{ width:{size*0.8}px; height:{size*0.8}px; }}
</style></head>
<body><img src="{url}"></body></html>"""
    
    html_path = f"{work_dir}/sourced/logo_{name}.html"
    Path(html_path).write_text(html)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": size, "height": size})
        page.goto(f"file://{html_path}")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=local_path, omit_background=True)
        browser.close()
    
    return local_path
```

## 2. devicon CDN (Fallback)

150+ programming language and dev tool logos with multiple variants.

```python
def get_devicon_url(name: str, variant: str = "original") -> str:
    """Get logo from devicon CDN.
    
    Variants: original, plain, line, original-wordmark, plain-wordmark
    """
    slug = name.lower().replace(" ", "").replace(".", "").replace("+", "plus")
    return f"https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{slug}/{slug}-{variant}.svg"
```

## 3. geticon.dev (Company Logos)

For company logos not in Simple Icons (startups, less common brands).

```python
def get_company_logo_url(domain: str) -> str:
    """Get company logo/favicon from geticon.dev."""
    return f"https://geticon.dev/?url={domain}"
```

Example: `https://geticon.dev/?url=vercel.com` returns Vercel's logo.

## 4. Playwright Screenshot (Last Resort)

For logos not available in any CDN:

```python
def screenshot_logo(search_query: str, work_dir: str) -> str:
    """Search Google Images for a logo and screenshot it."""
    local_path = f"{work_dir}/sourced/logo_screenshot_{search_query[:20]}.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 400, "height": 400})
        page.goto(f"https://www.google.com/search?q={search_query}+logo+png&tbm=isch")
        page.wait_for_load_state("networkidle")
        
        # Find first image result
        img = page.query_selector("img[data-src], img[src*='http']")
        if img:
            img.screenshot(path=local_path)
        
        browser.close()
    return local_path
```

## Logo Composition on Timeline

For `logo_composition` segments (multiple logos arranged):

```python
# Upload each logo individually
logos = []
for tech in ["react", "vue", "angular", "svelte"]:
    path = download_logo_as_png(tech, WORK_DIR)
    uploaded = asset_coll.upload(file_path=path, name=f"simpleicons_{tech}_logo")
    logos.append(uploaded)

# Create a dark background
bg = coll.generate_image(
    prompt="Solid dark navy blue background, subtle gradient, minimalist",
    aspect_ratio="16:9",
)

# Compose: background full-screen, logos at positions
main_track.add_clip(seg_start, Clip(asset=ImageAsset(id=bg.id), duration=seg_dur, fit=Fit.crop))

positions = [Position.top_left, Position.top_right, Position.bottom_left, Position.bottom_right]
for i, logo in enumerate(logos):
    overlay_track.add_clip(seg_start, Clip(
        asset=ImageAsset(id=logo.id),
        duration=seg_dur,
        scale=0.15,
        position=positions[i],
        offset=Offset(x=0.1, y=0.1),
        opacity=0.95,
    ))
```

## For Logo Badge Overlays

Single logo in corner during a segment:

```python
logo_path = download_logo_as_png("react", WORK_DIR, size=128)
logo_asset = asset_coll.upload(file_path=logo_path, name="simpleicons_react_logo")

overlay_track.add_clip(seg_start, Clip(
    asset=ImageAsset(id=logo_asset.id),
    duration=seg_dur,
    scale=0.08,
    position=Position.top_right,
    offset=Offset(x=-0.03, y=0.03),
    opacity=0.85,
))
```

## Upload to Asset Collection

After sourcing any logo, upload for future reuse:

```python
uploaded = asset_coll.upload(file_path=logo_path, name=f"simpleicons_{name}_logo")
```

Logos are images so no scene indexing needed — just descriptive naming for text-based search.
