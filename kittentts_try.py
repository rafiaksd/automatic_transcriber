import winsound, os
from kittentts import KittenTTS

print(f"🚩📦 Model Loading...")
m = KittenTTS("KittenML/kitten-tts-nano-0.1")
print(f"🏁📦 Model Loaded...")

#text_to_generate = "And this is the whole problem of puer is that if you are never willing to commit, if you never take the plunge, then you will never live life. You'll live, as Bane said, a provisional life, a halflife. There is always a probls."

with open('my_text.txt', 'r', encoding='utf-8') as file:
    text_to_generate = file.read()

print(f"🚩 Generation starting...")
audio = m.generate(text_to_generate, voice='expr-voice-4-m', speed=1.4)
print(f"🏁 Generation done")
# available_voices : [  'expr-voice-2-m', 'expr-voice-2-f', 'expr-voice-3-m', 'expr-voice-3-f',  'expr-voice-4-m', 'expr-voice-4-f', 'expr-voice-5-m', 'expr-voice-5-f' ]


sound_file = 'output.wav'
import soundfile as sf
sf.write(sound_file, audio, 24000)
print(f"✍️ Saved audio")

print(f"🎙️ Playing audio")
winsound.PlaySound(sound_file, winsound.SND_FILENAME) 

os.remove(sound_file)
print(f"🗑️🗑️ Audio deleted")