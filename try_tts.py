import edge_tts
import asyncio, time, os, re
import pygame

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
    pygame.mixer.music.play()

    # Wait until audio playback is done
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()

with open('text2.txt', 'r', encoding='utf-8') as file:
    text_to_generate = file.read()

text_to_generate = sanitize_text_for_tts(text_to_generate)

async def main():
    sound_file = "edge_output.mp3"

    tts = edge_tts.Communicate(text=text_to_generate, voice="en-US-GuyNeural", rate="+30%")
    await tts.save(sound_file)
    print(f"✅ Saved {sound_file}")

    play_audio_and_wait(sound_file)

    os.remove(sound_file)
    print(f"🗑️ Deleted {sound_file}")

asyncio.run(main())
