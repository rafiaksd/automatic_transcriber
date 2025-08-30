import subprocess

def convert_mp4_to_3gp(input_file, output_file):
    # FFmpeg command to convert MP4 to 3GP with 16kHz audio (AAC codec)
    command = [
        'ffmpeg',
        '-i', input_file,  # Input file
        '-vn',              # Disable video (only audio)
        '-ar', '16000',     # Set audio sample rate to 16 kHz
        '-ac', '1',         # Mono audio (1 channel)
        '-ab', '16k',       # Audio bitrate 64kbps for better quality
        '-c:a', 'aac',      # Use AAC codec for audio
        '-f', '3gp',        # Output format 3GP
        output_file         # Output file name
    ]
    
    # Run the command using subprocess
    subprocess.run(command, check=True)

# Example usage
input_file = 'recordings/REAL ANALYSIS WILL BREAK YOU.mp4'
output_file = 'recordings/output2.3gp'
convert_mp4_to_3gp(input_file, output_file)
