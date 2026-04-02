"""
News Digest Video Builder
Reads registry.json and assembles a professional news digest video using VideoDB.

Usage:
    python build_video.py <path-to-registry.json>

Architecture: 5-track timeline
    1. bg_track     — Background image (full duration, Fit.crop)
    2. visual_track — Content: images/videos (scale 0.75, Fit.contain, centered)
    3. text_track   — Section labels (Option C: white on blue box)
    4. audio_track  — Voiceovers (full volume)
    5. music_track  — Background music (15% volume, looped)

Structure: title (4s) → intro → 3 news clips → 3 tweets → 2 articles → outro (5s)
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(".env")

import videodb
from videodb.editor import (
    Timeline, Track, Clip,
    VideoAsset, ImageAsset, AudioAsset, TextAsset,
    Fit, Position, Transition,
    Font, Border, Shadow, Background, TextAlignment,
)

# ============================================================
# CONSTANTS
# ============================================================

TITLE_DUR = 4.0
OUTRO_DUR = 5.0
LABEL_DUR = 3.0   # text label shown before muted video preview during hooks
SCALE = 0.75      # content scale (padding around visuals)
FADE = Transition(in_="fade", out="fade", duration=0.5)
FADE_IN = Transition(in_="fade", duration=0.5)
FADE_OUT = Transition(out="fade", duration=0.5)


def make_text(text, size=88, width=None, height=None, max_chars_per_line=35):
    """Option C style: white text, wide blue box, white border, shadow.

    Auto-sizes background box to fit text if width/height not specified.
    Long single lines are automatically wrapped to max_chars_per_line.

    Formula: width ≈ longest_line × size × 0.65 + 40px padding
             height ≈ line_count × size × 1.3 + 30px padding
    """
    # Auto-wrap long lines
    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        if len(line) > max_chars_per_line:
            # Wrap long line into chunks
            words = line.split(' ')
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if len(test_line) <= max_chars_per_line:
                    current_line.append(word)
                else:
                    if current_line:
                        wrapped_lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                wrapped_lines.append(' '.join(current_line))
        else:
            wrapped_lines.append(line)

    text = '\n'.join(wrapped_lines)

    if width is None:
        lines = text.split('\n')
        longest_line = max(len(line) for line in lines)
        width = int(longest_line * size * 0.65 + 40)
        width = max(width, 400)  # minimum 400px
        width = min(width, 1600)  # maximum 1600px (safe for 1920px screen)

    if height is None:
        line_count = text.count('\n') + 1
        height = int(line_count * size * 1.3 + 30)
        height = max(height, 100)  # minimum 100px
        height = min(height, 500)  # maximum 500px (allow taller for wrapped text)

    return TextAsset(
        text=text,
        font=Font(family="Clear Sans", size=size, color="#FFFFFF", opacity=1.0),
        background=Background(
            width=width,
            height=height,
            color="#1a3a5c",
            opacity=0.90,
            text_alignment=TextAlignment.center,
        ),
        border=Border(color="#FFFFFF", width=2.0),
        shadow=Shadow(color="#000000", x=3, y=3),
    )


def build_video(registry_path: str) -> dict:
    """Build a news digest video from a registry.json file.

    Args:
        registry_path: Path to registry.json

    Returns:
        dict with stream_url, player_url, duration
    """
    reg = json.loads(Path(registry_path).read_text())

    conn = videodb.connect()

    bg = reg["background"]
    vids = reg["videos"]
    tweets = reg["tweets"]
    articles = reg["articles"]
    vo = reg["voiceovers"]

    # --- Calculate total duration ---
    content_dur = (
        TITLE_DUR
        + vo["intro"]["duration"]
        + vo["hook_1"]["duration"] + vids["video_1"]["clip_duration"]
        + vo["hook_2"]["duration"] + vids["video_2"]["clip_duration"]
        + vo["hook_3"]["duration"] + vids["video_3"]["clip_duration"]
        + vo["tweet_transition"]["duration"]
        + vo["tweet_1"]["duration"]
        + vo["tweet_2"]["duration"]
        + vo["tweet_3"]["duration"]
        + vo["article_transition"]["duration"]
        + vo["article_1"]["duration"]
        + vo["article_2"]["duration"]
    )
    total_dur = content_dur + OUTRO_DUR

    # --- Build timeline ---
    timeline = Timeline(conn)
    timeline.background = "#0d0d1a"
    timeline.resolution = "1920x1080"

    bg_track = Track()
    visual_track = Track()
    text_track = Track()
    audio_track = Track()
    music_track = Track()

    # Background image
    bg_track.add_clip(0, Clip(
        asset=ImageAsset(id=bg["image_id"]),
        duration=total_dur,
        fit=Fit.crop,
    ))

    # Background music looped at 15%
    music_len = bg["music_duration"]
    music_loops = int(total_dur // music_len) + 1
    for i in range(music_loops):
        start = i * music_len
        remaining = total_dur - start
        d = min(music_len, remaining)
        if d > 0:
            music_track.add_clip(start, Clip(
                asset=AudioAsset(id=bg["music_id"], volume=0.15),
                duration=d,
            ))

    t = 0.0

    # --- TITLE CARD ---
    text_track.add_clip(t, Clip(
        asset=make_text(
            reg["topic"].upper() + "\nNEWS DIGEST",
            size=96,  # auto-sizes width/height based on text length
        ),
        duration=TITLE_DUR,
        position=Position.center,
    ))
    t += TITLE_DUR

    # --- INTRO ---
    audio_track.add_clip(t, Clip(
        asset=AudioAsset(id=vo["intro"]["id"]),
        duration=vo["intro"]["duration"],
    ))
    # Show first tweet as intro visual
    visual_track.add_clip(t, Clip(
        asset=ImageAsset(id=tweets["tweet_1"]["image_id"]),
        duration=vo["intro"]["duration"],
        fit=Fit.contain, scale=SCALE, position=Position.center, transition=FADE,
    ))
    t += vo["intro"]["duration"]

    # --- 3 NEWS CLIPS ---
    for i in range(1, 4):
        vid = vids[f"video_{i}"]
        hook = vo[f"hook_{i}"]
        hook_dur = hook["duration"]
        preview_dur = hook_dur - LABEL_DUR
        clip_start = vid["clip_start"]
        clip_dur = vid["clip_duration"]
        preview_start = max(0, clip_start - preview_dur)

        # Text label (3s)
        text_track.add_clip(t, Clip(
            asset=make_text(vid["label"], size=88),  # auto-sizes
            duration=LABEL_DUR,
            position=Position.center,
        ))

        # Hook voiceover
        audio_track.add_clip(t, Clip(
            asset=AudioAsset(id=hook["id"]),
            duration=hook_dur,
        ))

        # Muted video preview after text
        visual_track.add_clip(t + LABEL_DUR, Clip(
            asset=VideoAsset(id=vid["video_id"], start=preview_start, volume=0),
            duration=preview_dur,
            fit=Fit.contain, scale=SCALE, position=Position.center, transition=FADE_IN,
        ))
        t += hook_dur

        # Actual clip with original audio
        visual_track.add_clip(t, Clip(
            asset=VideoAsset(id=vid["video_id"], start=clip_start, volume=1),
            duration=clip_dur,
            fit=Fit.contain, scale=SCALE, position=Position.center, transition=FADE,
        ))
        t += clip_dur

    # --- SOCIAL MEDIA ---
    text_track.add_clip(t, Clip(
        asset=make_text("SOCIAL MEDIA\nREACTIONS", size=80),  # auto-sizes
        duration=vo["tweet_transition"]["duration"],
        position=Position.center,
    ))
    audio_track.add_clip(t, Clip(
        asset=AudioAsset(id=vo["tweet_transition"]["id"]),
        duration=vo["tweet_transition"]["duration"],
    ))
    t += vo["tweet_transition"]["duration"]

    for i in range(1, 4):
        tw_vo = vo[f"tweet_{i}"]
        visual_track.add_clip(t, Clip(
            asset=ImageAsset(id=tweets[f"tweet_{i}"]["image_id"]),
            duration=tw_vo["duration"],
            fit=Fit.contain, scale=SCALE, position=Position.center, transition=FADE,
        ))
        audio_track.add_clip(t, Clip(
            asset=AudioAsset(id=tw_vo["id"]),
            duration=tw_vo["duration"],
        ))
        t += tw_vo["duration"]

    # --- ARTICLES ---
    text_track.add_clip(t, Clip(
        asset=make_text("DEEP ANALYSIS", size=80),  # auto-sizes
        duration=vo["article_transition"]["duration"],
        position=Position.center,
    ))
    audio_track.add_clip(t, Clip(
        asset=AudioAsset(id=vo["article_transition"]["id"]),
        duration=vo["article_transition"]["duration"],
    ))
    t += vo["article_transition"]["duration"]

    for i in range(1, 3):
        art = articles[f"article_{i}"]
        art_vo = vo[f"article_{i}"]
        art_dur = art_vo["duration"]
        scroll_dur = art["scroll_duration"]
        screenshot_dur = art_dur - scroll_dur

        audio_track.add_clip(t, Clip(
            asset=AudioAsset(id=art_vo["id"]),
            duration=art_dur,
        ))
        visual_track.add_clip(t, Clip(
            asset=VideoAsset(id=art["scroll_id"], volume=0),
            duration=scroll_dur,
            fit=Fit.contain, scale=SCALE, position=Position.center, transition=FADE_IN,
        ))
        visual_track.add_clip(t + scroll_dur, Clip(
            asset=ImageAsset(id=art["screenshot_id"]),
            duration=screenshot_dur,
            fit=Fit.contain, scale=SCALE, position=Position.center, transition=FADE_OUT,
        ))
        t += art_dur

    # --- OUTRO ---
    text_track.add_clip(t, Clip(
        asset=make_text("POWERED BY VIDEODB", size=80),  # auto-sizes
        duration=OUTRO_DUR,
        position=Position.center,
    ))

    # --- ASSEMBLE ---
    timeline.add_track(bg_track)
    timeline.add_track(visual_track)
    timeline.add_track(text_track)
    timeline.add_track(audio_track)
    timeline.add_track(music_track)

    stream_url = timeline.generate_stream()
    total = t + OUTRO_DUR

    result = {
        "stream_url": stream_url,
        "player_url": f"https://console.videodb.io/player?url={stream_url}",
        "duration_seconds": round(total, 1),
        "duration_formatted": f"{int(total // 60)}:{int(total % 60):02d}",
    }
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_video.py <path-to-registry.json>")
        sys.exit(1)

    registry_path = sys.argv[1]
    result = build_video(registry_path)

    # Save output.json in output/ folder (sibling of data/)
    topic_dir = Path(registry_path).parent.parent  # data/ -> topic-slug/
    output_dir = topic_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "output.json"
    output_path.write_text(json.dumps(result, indent=2))

    print(json.dumps(result, indent=2))
    print(f"\nPlayer: {result['player_url']}")
