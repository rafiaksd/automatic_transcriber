import yt_dlp
import os, re, time, winsound, subprocess
import ollama

model_ollama = "granite3.3:8b" #gpt-oss:20b #mistral:7b #granite3.3:8b
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
    """Summarizes YouTube captions with balanced clarity, depth, and simplicity."""
    response = ollama.chat(
        model=model_ollama,
        messages=[
            {
                'role': 'user',
                'content': (
                    "Summarize the following text in a way that is clear, easy to understand, and intellectually engaging.\n"
                    "The summary should not be too short or overly concise. It should provide enough detail to carry depth and meaning, "
                    "but still be easy to follow. Use complete sentences with simple, everyday words that a 10-year-old could understand — "
                    "but craft it in a way that feels powerful, thoughtful, and mind-stimulating.\n"
                    "Avoid fluff, avoid over-explaining, and avoid any questions, suggestions, or extra commentary. Just return the summary.\n\n"
                    f"{text}"
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

print(f"🧠🧠 Model using: {model_ollama}")
print(f"🚩🚩 STARTING SUMMARIZING {title}")
summarized_text = summarize_text(subtitles_text)

summarized_text_filename = f"{title}_summarized.md"
with open(f"summaries/{summarized_text_filename}", "w", encoding="utf-8") as f:
     f.write(summarized_text)
print(f"\n✅ SUMMARY saved to: {summarized_text_filename}")

summarized_file = f"summaries/{summarized_text_filename}"

get_time_lapsed(very_start_time, "🏁🏁🏁 TOTAL WORK")

print(f"FINISHED")
winsound.Beep(1000,1000)

#####################
## Text to Speech ###
#####################
import edge_tts
import asyncio, time, os, re
import pygame

tts_speed_change = 60

def sanitize_text_for_tts(text):
    # Replace smart quotes with plain quotes
    text = text.replace('“', '"').replace('”', '"').replace("’", "'")

    # Remove asterisks and dashes
    text = re.sub(r'[\*\-]', '', text)

    # Remove markdown-style headings (e.g. **Heading**)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)

    # Replace multiple spaces or newlines with single space or newline
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Strip leading/trailing spaces
    text = text.strip()

    return text

def play_audio_and_wait(audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)

    winsound.PlaySound("success.wav", winsound.SND_FILENAME)
    input("👆👆👀 Press anything to play...")
    
    subprocess.Popen(['notepad.exe', summarized_file])
    pygame.mixer.music.play()

    # Wait until audio playback is done
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()

with open(summarized_file, 'r', encoding='utf-8') as file:
    text_to_generate = file.read()
text_to_generate = sanitize_text_for_tts(text_to_generate)

async def main():
    sound_file = "edge_output.mp3"

    tts = edge_tts.Communicate(text=text_to_generate, voice="en-US-GuyNeural", 
                               rate=f"+{str(tts_speed_change)}%")
    await tts.save(sound_file)
    print(f"✅ Saved {sound_file}")
    play_audio_and_wait(sound_file)

    #os.remove(sound_file)
    #print(f"🗑️🗑️ Deleted {sound_file}")

asyncio.run(main())