import subprocess, time, os
import tkinter as tk
from tkinter import filedialog, simpledialog
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pydub import AudioSegment
from pytubefix import YouTube
from timerangebox import TimeRangeDialog

def download_youtube_video():
    link = simpledialog.askstring("YouTube Link", "Enter the YouTube video URL:")
    if not link:
        print("❌ No link provided.")
        return None

    try:
        yt = YouTube(link)

        # Try to get the 360p mp4 progressive stream
        stream = yt.streams.filter(res="360p", file_extension='mp4', progressive=True).first()

        # If 360p is not available, choose the highest resolution available
        if not stream:
            print("❌ 360p not available, selecting highest available resolution.")
            stream = yt.streams.filter(file_extension='mp4', progressive=True).get_highest_resolution()

        # Create folder if it doesn't exist
        save_path = os.path.join("Media", "Youtube")
        os.makedirs(save_path, exist_ok=True)

        # Download the video
        output_path = stream.download(output_path=save_path)
        print(f"✅ Video downloaded: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error downloading video 😱😱: {e}")
        return None

# Function to convert MP4 to MP3
def convert_mp4_to_mp3(input_file, folder_to_save):
    output_name = simpledialog.askstring("Input", "Enter the name for the output MP3 file:")

    if not output_name:
        print("No output name provided.")
        return None

    if not output_name.endswith(".mp3"):
        output_name += ".mp3"

    # Ask whether to use a custom time range
    use_custom_range = tk.messagebox.askyesno("Select Range", "Do you want to convert a custom time range?")

    if use_custom_range:
        try:
            # Use the TimeRangeDialog instead of asking for raw input
            root = tk.Tk()
            root.withdraw()  # Hide the main root window
            dialog = TimeRangeDialog(root)
            root.destroy()   # Destroy the hidden root after dialog is closed

            if not dialog.result:
                print("❌ Time range selection was cancelled.")
                return None

            start_secs, end_secs = dialog.result
            duration_secs = end_secs - start_secs
            
            # Convert to MP3
            mp3_path = os.path.join(folder_to_save, output_name)
            subprocess.run([
                'ffmpeg', '-ss', str(start_secs), '-t', str(duration_secs), '-i', input_file,
                '-loglevel', 'error', '-vn', mp3_path
            ])
            print(f"🟢 MP3 created for range {start_secs} - {end_secs}: {output_name}")

            # Ask if user also wants the video
            also_export_video = tk.messagebox.askyesno("Export Video", "Do you also want the MP4 video for that range?")
            if also_export_video:
                video_output_name = os.path.splitext(output_name)[0] + ".mp4"
                video_path = os.path.join(folder_to_save, video_output_name)
                subprocess.run([
                    'ffmpeg', '-ss', str(start_secs), '-t', str(duration_secs), '-i', input_file,
                    '-loglevel', 'error', '-c', 'copy', video_path
                ])
                print(f"🟢 MP4 video created: {video_output_name}")
            
            return mp3_path  # Return the audio path for transcription

        except Exception as e:
            print(f"❌ Invalid time range: {e}")
            return None

    else:
        # Convert full MP4 to MP3
        mp3_path = os.path.join(folder_to_save, output_name)
        subprocess.run(['ffmpeg', '-i', input_file, '-loglevel', 'error', '-vn', mp3_path])
        print(f"🟢 Full MP3 created: {output_name}")
        return mp3_path

# Folder to save media files
uni_folder_name = 'Media/'
inner_audio_folder = 'Audio/'

super_time_start = time.time()

def transcribe_audio(audio_file, audio_name, chunk_length_ms=30000, overlap_ms=2000):
    # Setup
    torch.set_num_threads(6)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    ).to(device)

    processor = AutoProcessor.from_pretrained(model_id)
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        #generate_kwargs={"return_timestamps": True},
    )

    # Load and split audio with overlap
    print("\n▶️▶️▶️   Loading and splitting audio with overlap...")
    audio = AudioSegment.from_file(audio_file)
    step = chunk_length_ms - overlap_ms
    chunks = []

    for i in range(0, len(audio), step):
        chunk = audio[i:i + chunk_length_ms]
        chunks.append(chunk)

    transcriptions = []
    transcribe_start_time = time.time()

    for idx, chunk in enumerate(chunks):
        chunk_path = f"{uni_folder_name}TempChunk/temp_chunk_{idx}.wav"
        chunk.export(chunk_path, format="wav")
        chunk_time = time.time()

        print(f"✂️📝 Transcribe Chunk {idx + 1}/{len(chunks)}... ", end="", flush=True)
        result = pipe(chunk_path)
        chunk_done_time = time.time()
        chunk_took_time = chunk_done_time - chunk_time
        abs_took_time = chunk_done_time - transcribe_start_time

        print(f"⏰ {abs_took_time:.2f}s ({chunk_took_time:.2f}s)")
        
        transcriptions.append(result["text"])

        os.remove(chunk_path)  # Clean up

    # You may later deduplicate or smooth overlaps if needed.
    full_transcription = " ".join(transcriptions)

    time_took = time.time() - transcribe_start_time
    estimated_token = len(full_transcription.split()) * 1.3
    print(f"\n⏰ Done in {time_took:.2f}s | Estimated Tokens: {estimated_token:.0f} | ⚡ Token Speed:{estimated_token / time_took:.2f}/s")

    # Save output
    output_path = f"{uni_folder_name}{audio_name}.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_transcription)

    print(f"💾 Saved transcription to {output_path}")
    return full_transcription, audio_name

# Set up tkinter root window (hidden)
root = tk.Tk()
root.withdraw()  # Don't show the main window

# Step 1: Open file dialog to select the audio or video file
file_to_process = None
download_from_youtube = tk.messagebox.askyesno("YouTube", "Do you want to download a video from YouTube first?")

if download_from_youtube:
    file_to_process = download_youtube_video()
else:
    file_to_process = filedialog.askopenfilename(
        title="Select an MP4 or MP3 file", 
        filetypes=[("MP4 files", "*.mp4"), ("MP3 files", "*.mp3")]
    )

transcribed = ('', '')

if file_to_process:
    file_extension = file_to_process.split('.')[-1].lower()

    if file_extension == "mp4":
        converted_audio_dir = os.path.join(uni_folder_name, inner_audio_folder)
        os.makedirs(converted_audio_dir, exist_ok=True)
        converted_to_mp3_file = convert_mp4_to_mp3(file_to_process, converted_audio_dir)
        if converted_to_mp3_file:
            converted_file_name = os.path.splitext(os.path.basename(converted_to_mp3_file))[0]
            transcribed = transcribe_audio(converted_to_mp3_file, converted_file_name)

    elif file_extension == "mp3":
        file_name_only = os.path.splitext(os.path.basename(file_to_process))[0]
        print(f'Selected {file_name_only}.mp3')
        transcribed = transcribe_audio(file_to_process, file_name_only)
    

print("FINISHED TRANSCRIBE! 💥💥💥")
#print(f"Now Transcribed: {transcribed[0]} | GOT File Name: {transcribed[1]}")

###################################################
###################################################
############# BEGIN TRANSLATION ##################
###################################################
###################################################

import sys, time, json, re, os, requests

translate_file_name = transcribed[1]
transcribed_arabic_text = transcribed[0]

if len(transcribed_arabic_text) < 5:
    raise ValueError("💀💀💀 No transcription happened, exiting...")

model_name = sys.argv[1] if len(sys.argv) > 1 else None
model = model_name or "qwen2.5:7b-instruct" #qwen2.5:7b-instruct, qwen2.5:14b-instruct-q3_K_M
print(f"🧮🧮🧮 Using model: {model}")

def sanitize_model_name(model_name: str) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', model_name)
    return sanitized

#file_to_read = "testnew.txt"
output_file = f"{translate_file_name}_translation_{sanitize_model_name(model)}.txt"  # Define the output file name
translation_folder = 'Translation/'

instruction = """Translate the following Arabic subtitles into English. Whenever the phrase "peace be upon him" appears, replace it with "ﷺ". Whenever the word 'God' appears, replace it with "Allah". End the translation after rendering all input.
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
print('\n💬📙📙 Started Streaming Translation...')
wait_start = time.time()
streaming_response = generate_streaming_response(prompt)
print(f"⏳ Delay to Start Translation: {time.time() - wait_start:.2f}s\n")
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
    print(f"🏆🏆🏆 FINISHED TRANSLATION 🏆🏆🏆 | TOTAL TIME : ⏱️⏱️⏱️ {super_time_took:.2f}s\n")

    # 🔓 Open file in default editor (Notepad on Windows)
    cwd = os.getcwd()
    complete_file_path = cwd + '/' + save_translation_file_name
    os.startfile(complete_file_path)
except Exception as e:
    print(f"\n⚠️⚠️⚠️ Error saving to file: {e}")