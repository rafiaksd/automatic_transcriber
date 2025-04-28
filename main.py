import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import time
import os

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
    torch.set_num_threads(8)  # Set to 8 threads for CPU
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
    print('\n🔍🔍🔍 started audio parsing...')
    result = pipe(audio_file)
    time_took = time.time() - start

    print(f"\n⏰⏰ Time took: {time_took:.2f}s")
    #print(f"🧐🧐🧐 The RESULT: {result}")
    transcription = result["text"]

    # Create a text file with the audio file name (without the extension)
    text_file_name = f"{uni_folder_name}{audio_name}.txt"

    # Save only the transcription to the text file
    with open(text_file_name, "w", encoding="utf-8") as file:
        file.write(transcription)

    print(f"💾💾💾 Transcription saved to {text_file_name}")

# Set up tkinter root window (hidden)
root = tk.Tk()
root.withdraw()  # Don't show the main window

# Step 1: Open file dialog to select the audio or video file
file_to_process = filedialog.askopenfilename(
    title="Select an MP4 or MP3 file", 
    filetypes=[("MP4 files", "*.mp4"), ("MP3 files", "*.mp3")]
)

if file_to_process:
    # Step 2: Check if the selected file is an MP4 or MP3
    file_extension = file_to_process.split('.')[-1].lower()

    if file_extension == "mp4":
        converted_audio_dir = uni_folder_name + inner_audio_folder
        converted_to_mp3_file = convert_mp4_to_mp3(file_to_process, converted_audio_dir)
        converted_file_name = converted_to_mp3_file.split('/')[-1].split('.')[0]
        print(f"CONVERTED FILE😱😱: {converted_file_name}.mp3")
        if converted_to_mp3_file:
            transcribe_audio(converted_to_mp3_file, converted_file_name)
    elif file_extension == "mp3":
        output_name = simpledialog.askstring("Input", "Enter the name for the TXT file:")
        transcribe_audio(file_to_process, output_name)
else:
    print("❌❌❌ No file selected")
