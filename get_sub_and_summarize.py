import yt_dlp
import os, re, time, winsound, subprocess
import ollama

model_ollama = "gemma3:4b"
print(f"🧠🧠 Model using: {model_ollama}")
very_start_time = time.time()

def get_time_lapsed(start_time, emojis="⏰⏱️"):
    now_time = time.time()
    time_elapse = now_time - start_time
    print(f"{emojis}  ⏰⏱️⏰ {time_elapse:.2f} seconds\n")
    return round(time_elapse, 2)

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

    return video_title, ' '.join(cleaned_text), f"{video_title}.txt"

def summarize_text(text):
    """Summarizes YouTube captions with depth, clarity, and engagement."""
    response = ollama.chat(
        model=model_ollama,
        messages=[
            {
                'role': 'user',
                'content': (
                    "Your task is to summarize it in full sentences that are clear, engaging, and thoughtful.\n\n"
                    "Focus on:\n"
                    "- Identifying the key themes or sections of the video\n"
                    "- Summarizing the main ideas and insights under each theme\n"
                    "- Using powerful and clear language that stimulates the reader’s understanding\n"
                    "- Writing in full sentences and structured in short paragraphs; absolutely do not use bullet points.\n"
                    "- The goal is make the summary meaningful, digestible insight\n"
                    "Make the summary feel like a thoughtful overview that helps the reader truly learn something even without reading it whole.\n\n"
                    "Here is the text you have to summarize:\n"
                    f"{text}\n\n"
                    "/no_think"
                ),
            },
        ],
    )
    return response['message']['content']


##################
## GET CAPTION ###
##################

video_url = input("Enter YouTube video URL: ")
title, subtitles_text, filename = get_clean_subtitles(video_url)

print(f"\n=== Video Title: {title} ===\n")

with open(f"subtitles/{filename}", "w", encoding="utf-8") as f:
     f.write(subtitles_text)
print(f"\n✅ Subtitles saved to: {filename}")
get_time_lapsed(very_start_time, "🏁🏁🏁 SUBTITLE DOWNLOAD FINISHED")

################
## SUMMARIZE ###
################

print(f"🚩🚩 STARTING SUMMARIZING {title}")
summarized_text = summarize_text(subtitles_text)

summarized_text_filename = f"{title}_summarized.md"
with open(f"summaries/{summarized_text_filename}", "w", encoding="utf-8") as f:
     f.write(summarized_text)
print(f"\n✅ Subtitles saved to: {summarized_text_filename}")

summarized_file = f"summaries/{summarized_text_filename}"
subprocess.Popen(['notepad.exe', summarized_file])

get_time_lapsed(very_start_time, "🏁🏁🏁 TOTAL WORK")

print(f"FINISHED")
winsound.Beep(1000,1000)