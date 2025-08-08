from kokoro import KPipeline
import soundfile as sf
import winsound, os

pipeline = KPipeline(lang_code='a')

with open('my_text.txt', 'r', encoding='utf-8') as file:
    text_to_generate = file.read()

#am_adam, am_fenrir, am_michael, am_puck, ... am_echo
generator = pipeline(text_to_generate, voice='am_echo', speed=1.3)

for i, (graphemes, phonemes, audio) in enumerate(generator):
    sound_file = f'{i}.wav'
    sf.write(sound_file, audio, 24000)
    print(f"Audio saved to {i}.wav")

    print(f"🎙️ Playing audio")
    winsound.PlaySound(sound_file, winsound.SND_FILENAME) 

    os.remove(sound_file)