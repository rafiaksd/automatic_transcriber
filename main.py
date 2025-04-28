import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import time

super_time_start = time.time()

# Function to convert MP4 to MP3
def convert_mp4_to_mp3(input_file, folder_to_save):
    output_name = simpledialog.askstring("Input", "Enter the name for the output MP3 file:")
    
    if output_name:
        # Add .mp3 extension if not present
        if not output_name.endswith(".mp3"):
            output_name += ".mp3"
        
        # Run FFmpeg command to convert mp4 to mp3
        subprocess.run(['ffmpeg', '-i', input_file, folder_to_save + output_name])
        print(f"Converted {input_file} to {output_name}")
        return folder_to_save + output_name
    else:
        print("No output name provided.")
        return None

# Folder to save media files
uni_folder_name = 'Media/'
inner_audio_folder = 'Audio/'

# Function to transcribe audio (MP3)
def transcribe_audio(audio_file, audio_name):
    # Initialize model and pipeline
    #torch.set_num_threads(8)  # Set to 8 threads for CPU

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        generate_kwargs={"return_timestamps": True},
    )

    start = time.time()
    print('\n▶️▶️▶️ started audio parsing...')
    result = pipe(audio_file)
    time_took = time.time() - start

    #print(f"🧐🧐🧐 The RESULT: {result}")
    transcription = result["text"]
    estimated_token = len(transcription.split(' '))

    print(f"\n⏰⏰ Time took: {time_took:.2f}s | Tokens: {estimated_token} | ⚡ Token Speed: {estimated_token/time_took:.2f}/s")

    # Create a text file with the audio file name (without the extension)
    text_file_name = f"{uni_folder_name}{audio_name}.txt"

    # Save only the transcription to the text file
    with open(text_file_name, "w", encoding="utf-8") as file:
        file.write(transcription)

    print(f"💾💾💾 Transcription saved to {text_file_name}")

    return (transcription, audio_name)

# Set up tkinter root window (hidden)
root = tk.Tk()
root.withdraw()  # Don't show the main window

# Step 1: Open file dialog to select the audio or video file
file_to_process = filedialog.askopenfilename(
    title="Select an MP4 or MP3 file", 
    filetypes=[("MP4 files", "*.mp4"), ("MP3 files", "*.mp3")]
)

transcribed = ('', '')

if file_to_process:
    # Step 2: Check if the selected file is an MP4 or MP3
    file_extension = file_to_process.split('.')[-1].lower()

    if file_extension == "mp4":
        converted_audio_dir = uni_folder_name + inner_audio_folder
        converted_to_mp3_file = convert_mp4_to_mp3(file_to_process, converted_audio_dir)
        converted_file_name = converted_to_mp3_file.split('/')[-1].split('.')[0]
        print(f"CONVERTED FILE 🔄🔄🔄: {converted_file_name}.mp3")
        if converted_to_mp3_file:
            transcribed = transcribe_audio(converted_to_mp3_file, converted_file_name)
    elif file_extension == "mp3":
        output_name = simpledialog.askstring("Input", "Enter the name for the TXT file:")
        transcribed = transcribe_audio(file_to_process, output_name)
else:
    print("❌❌❌ No file selected")
    

print("FINISHED TRANSCRIBE! 💥💥💥")
#print(f"Now Transcribed: {transcribed[0]} | GOT File Name: {transcribed[1]}")

###################################################
###################################################
############# BEGIN TRANSLATION ##################
###################################################
###################################################

import sys

translate_file_name = transcribed[1]
transcribed_arabic_text = transcribed[0]

if len(transcribed_arabic_text) < 5:
    raise ValueError("💀💀💀 No transcription happened, exiting...")

model_name = sys.argv[1] if len(sys.argv) > 1 else None
model = model_name or "qwen2.5:7b" #qwen2.5:14b-instruct-q3_K_M
print(f"🧮🧮🧮 Using model: {model}")

import requests
import time, json, re, os

def sanitize_model_name(model_name: str) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', model_name)
    return sanitized

#file_to_read = "testnew.txt"
output_file = f"{translate_file_name}_translation_{sanitize_model_name(model)}.txt"  # Define the output file name
translation_folder = 'Translation/'

instruction = """Translate the following Arabic subtitles into English, maintaining the original sentence order. Present the translation in standard paragraph form, without numbering. Whenever the phrase "peace be upon him" appears, replace it with "ﷺ". Whenever the word 'God' appears, replace it with "Allah". Ensure the English translation accurately reflects the meaning of the Arabic text while striving to preserve the sequence of the original sentences. The input may contain consecutive text segments that should be translated in order. End the translation after rendering all input.
"""

#with open(f"Media/{file_to_read}", "r", encoding="utf-8") as file:
    #content = file.read()

arabic_text = transcribed_arabic_text

prompt = instruction + arabic_text

# Send request to Ollama API with streaming enabled
def generate_streaming_response(own_prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": own_prompt,
            "temperature": 0.6,
            "stream": True,
        },
        stream=True,
    )
    return response

start = time.time()
print('\n💬📙📙 started streaming translation...')
streaming_response = generate_streaming_response(prompt)
full_translation = ""  # Initialize an empty string to store the full translation

# Check and print streaming result
if streaming_response.status_code == 200:
    print("Streaming Translation:📖📖\n")
    try:
        for line in streaming_response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                try:
                    json_data = json.loads(decoded_line)
                    response_part = json_data.get('response', '')
                    print(response_part, end='', flush=True)
                    full_translation += response_part  # Append the current part to the full translation
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {decoded_line}")
        print()  # Add a newline at the end of the stream
    except requests.exceptions.RequestException as e:
        print(f"Error during streaming: {e}")
else:
    print("Error:", streaming_response.status_code, streaming_response.text)

time_took = time.time() - start
token_speed = (len(full_translation.split(' ')))/time_took

print(f"\n⏰ Total time: {time_took:.2f}s | ⚡ Token Speed:{token_speed:.2f}/s")

save_translation_file_name = translation_folder + output_file
# Save the full translation to a file
try:
    with open(save_translation_file_name, "w", encoding="utf-8") as outfile:
        outfile.write(full_translation)
    print(f"\n💾💾💾 Translation saved to: {save_translation_file_name}")

    #finished
    super_time_end = time.time()
    super_time_took = super_time_end - super_time_start
    print(f"🏆🏆🏆 FINISHED TRANSLATION 🏆🏆🏆 | TOTAL TIME : ⏱️⏱️⏱️ {super_time_took:.2f}s")

    # 🔓 Open file in default editor (Notepad on Windows)
    cwd = os.getcwd()
    complete_file_path = cwd + '/' + save_translation_file_name
    os.startfile(complete_file_path)
except Exception as e:
    print(f"\n⚠️⚠️⚠️ Error saving to file: {e}")