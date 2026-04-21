# Asset Library (VideoDB Collection Cache)

A persistent VideoDB collection that acts as a searchable cache of previously sourced real-world assets. **Always search here first** before sourcing from external APIs or generating with AI.

## Collection Constant

```python
ASSET_COLLECTION_NAME = "content_creator_assets"
```

This collection persists across all video runs. Every time you source a real-world asset (stock footage, meme, logo, GIF), upload it here for future reuse.

## Phase 0: Bootstrap

During pre-flight, find or create the collection:

```python
import videodb

conn = videodb.connect()

# Find existing collection
asset_coll = None
for c in conn.get_collections():
    if c.name == ASSET_COLLECTION_NAME:
        asset_coll = c
        break

# Create if not found
if asset_coll is None:
    asset_coll = conn.create_collection(name=ASSET_COLLECTION_NAME)
    print(f"Created asset collection: {asset_coll.id}")
else:
    print(f"Using existing asset collection: {asset_coll.id} ({len(asset_coll.get_videos())} videos, {len(asset_coll.get_images())} images)")
```

## Search Pattern: Before Every Sourcing Decision

Before hitting any external API, search the collection. If a good match exists, use it instantly — it's free, fast, and already uploaded.

### Search videos (stock footage, motion scenes, reaction GIFs)

```python
from videodb import SearchType

results = asset_coll.search(
    query="developer confused looking at screen",
    search_type=SearchType.semantic,
)

if results and len(results.get_shots()) > 0:
    best_shot = results.get_shots()[0]
    print(f"Found cached asset: {best_shot.video_id} ({best_shot.start}-{best_shot.end}s, score: {best_shot.search_score})")
    if best_shot.search_score > 0.5:
        # Use this asset directly
        video = asset_coll.get_video(best_shot.video_id)
        # Use video.id in your timeline
```

### Search images (memes, logos, photos)

Images don't have temporal content, so they rely on descriptive naming. Search by listing and matching names:

```python
images = asset_coll.get_images()
query_lower = "drake meme".lower()

matches = [img for img in images if query_lower in img.name.lower()]
if matches:
    # Use matches[0].id directly
    print(f"Found cached image: {matches[0].name}")
```

### Score Threshold

| Score | Action |
|-------|--------|
| > 0.6 | Use directly — strong match |
| 0.4-0.6 | Use if no better external option found quickly |
| < 0.4 | Skip — source fresh from external API |

## Upload Pattern: After Sourcing Any Asset

Every time you download an asset from an external API (Pexels, Imgflip, GIPHY, Simple Icons), upload it to the collection with a descriptive name.

### Upload video assets

```python
# After downloading from Pexels/GIPHY to a local path
uploaded = asset_coll.upload(
    file_path=local_video_path,
    name="pexels_developer_typing_at_desk_1280x720",
)

# Index scenes for future semantic search
uploaded.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 2, "select_frames": ["first"]},
    prompt="Describe what this video clip shows. Include: subject, action, setting, mood.",
)
print(f"Uploaded + indexed: {uploaded.id}")
```

### Upload image assets

```python
# After downloading from Imgflip/Pexels/Simple Icons
uploaded_img = asset_coll.upload(
    file_path=local_image_path,
    name="imgflip_drake_meme_template",
)
print(f"Uploaded image: {uploaded_img.id}")
```

### Upload from URL

```python
# If you have a direct URL (e.g., from Pexels API response)
uploaded = asset_coll.upload(url=direct_url, name="pexels_city_night_aerial")
```

## Naming Convention

Use descriptive names that enable future text matching:

```
{source}_{description}_{resolution_or_format}
```

Examples:
- `pexels_developer_typing_dark_office_1280x720`
- `imgflip_drake_meme_template`
- `giphy_facepalm_reaction_mp4`
- `simpleicons_react_logo_svg`
- `pexels_aerial_city_night_neon_1920x1080`
- `giphy_mind_blown_explosion_mp4`

## When NOT to Cache

- One-off Remotion renders (unique to this video's content)
- TextAssets (generated fresh each time, trivial)
- Code screenshots (specific to this video's code)
- Browser captures (time-sensitive content)

## Collection Maintenance

The collection grows over time. This is fine — VideoDB handles large collections efficiently. The more assets cached, the less external API calls needed in future videos.

If the collection becomes very large (1000+ items), consider:
- More specific search queries to narrow results
- Using video descriptions and names for filtering before semantic search
