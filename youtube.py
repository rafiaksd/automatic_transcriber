import sys 
from pytubefix import YouTube

url_link = sys.argv[1] if len(sys.argv) > 1 else None

print(f'Len: {len(sys.argv)}')
if len(sys.argv) < 2:
    raise ValueError("❌❌❌ Enter a YouTube Link, exiting...")

# Replace with your desired YouTube video URL
url = url_link

yt = YouTube(url)

# Select the 360p stream
ys = yt.streams.get_by_resolution("360p")

# Download the video
ys.download(output_path="./Media/Downloads")
