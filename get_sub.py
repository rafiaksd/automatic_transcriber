import yt_dlp
import os
import re

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '', name)

def get_clean_subtitles(video_url: str) -> tuple[str, str, str]:
    """
    Downloads and cleans English subtitles from a YouTube video.
    Returns a tuple: (video_title, clean_subtitle_text, filename_used)
    """
    ydl_opts = {
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'writeautomaticsub': True,
        'skip_download': True,
        'outtmpl': '%(id)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        video_id = info.get('id')
        video_title = sanitize_filename(info.get('title'))
        subtitle_file = f"{video_id}.en.vtt"

    if not os.path.exists(subtitle_file):
        raise FileNotFoundError("❌ Subtitle file not found.")

    with open(subtitle_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_text = []
    seen_lines = set()

    for line in lines:
        line = line.strip()

        if (
            line == '' or
            line.startswith('WEBVTT') or
            line.startswith('Kind:') or
            line.startswith('Language:') or
            '-->' in line or
            re.match(r'^\d+$', line)
        ):
            continue

        line = re.sub(r'<[^>]+>', '', line)

        if line and line not in seen_lines:
            cleaned_text.append(line)
            seen_lines.add(line)

    # Clean up downloaded subtitle file
    os.remove(subtitle_file)

    return video_title, '\n'.join(cleaned_text), f"{video_title}.txt"

video_url = input("Enter YouTube video URL: ")
title, subtitles_text, filename = get_clean_subtitles(video_url)

print(f"\n=== Video Title: {title} ===\n")

shortened_text = ' '.join(subtitles_text.split()[:10])

# Save manually if you want
with open(filename, "w", encoding="utf-8") as f:
     f.write(subtitles_text)
print(f"\n✅ Subtitles saved to: {filename}")

