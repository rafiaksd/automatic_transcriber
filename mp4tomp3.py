import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog

folder_to_save = 'Media/'
# Set up tkinter root window (hidden)
root = tk.Tk()
root.withdraw()  # Don't show the main window

# Step 1: Open file dialog to select the MP4 file
input_file = filedialog.askopenfilename(title="Select an MP4 file", filetypes=[("MP4 files", "*.mp4")])

# Check if a file was selected
if input_file:
    # Step 2: Prompt the user to enter the output name for the MP3 file
    output_name = simpledialog.askstring("Input", "Enter the name for the output MP3 file:")
    
    # Check if the user provided a name
    if output_name:
        # Add .mp3 extension if not present
        if not output_name.endswith(".mp3"):
            output_name += ".mp3"
        
        # Step 3: Run FFmpeg command to convert mp4 to mp3
        subprocess.run(['ffmpeg', '-i', input_file, folder_to_save + output_name])
        
        print(f"Converted {input_file} to {output_name}")
    else:
        print("No output name provided.")
else:
    print("No file selected")
