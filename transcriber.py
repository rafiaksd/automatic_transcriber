from faster_whisper import WhisperModel
import time, os, datetime, winsound

print("🧠🧠 Loading model")
model_size = "large-v3-turbo"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

######################
## helper functions ##
######################

import numpy as np

def get_time_lapsed(start_time, emojis="⏰⏱️"):
    now_time = time.time()
    time_elapse = now_time - start_time
    print(f"{emojis}\tTime elapsed: {time_elapse:.2f} seconds\n")
    return round(time_elapse, 2)

def format_time(seconds):
    return str(datetime.timedelta(seconds=int(seconds)))

###################
### select file ###
###################

input_file = "recordings/output2.3gp"
print(f"📦📦 Selected: {input_file}")

input_file_name = input_file.split(".")[0]

###################
## transcription ##
###################

transcription_start_time = time.time()

print("♨️♨️ Started SENTENCE LEVEL Transcribing...\n")

segments, info = model.transcribe(input_file, word_timestamps=False, beam_size=5, vad_filter=True)

sentence_segments = []
for segment in segments:
    sentence_segments.append(segment)

base_filename = os.path.splitext(os.path.basename(input_file))[0]
output_file = os.path.join(f"{base_filename}_transcribed.txt")
transcribed_text = ""

with open(output_file, "w", encoding="utf-8") as f:
    for i, seg in enumerate(sentence_segments):
        start = format_time(seg.start)
        end = format_time(seg.end)
        #line = f"[{i+1}] {start} - {end}: {seg.text}"
        line = f"{start} - {end}: {seg.text}"
        #print(line)
        f.write(line + "\n")
        transcribed_text += line + "\n"

get_time_lapsed(transcription_start_time)

print(transcribed_text)
winsound.Beep(1000,500)