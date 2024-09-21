import os
import yt_dlp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Function to download YouTube video
def download_video(url, output_path='video.mp4'):
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'cookiefile': 'cookies.txt',  # Path to your cookies file
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return info_dict

# Function to extract chapters
def extract_chapters(video_path, chapters, output_dir='chapters'):
    os.makedirs(output_dir, exist_ok=True)
    for chapter in chapters:
        start_time = chapter['start_time']
        end_time = chapter['end_time']
        title = chapter['title'].replace(" ", "_")
        output_path = os.path.join(output_dir, f"{title}.mp4")
        ffmpeg_extract_subclip(video_path, start_time, end_time, targetname=output_path)

# Main script
if __name__ == "__main__":
    url = input("Enter YouTube video URL: ")
    video_path = 'video.mp4'
    
    try:
        info_dict = download_video(url, video_path)
        chapters = []
        if 'chapters' in info_dict:
            for chapter in info_dict['chapters']:
                chapters.append({
                    'title': chapter['title'],
                    'start_time': chapter['start_time'],
                    'end_time': chapter['end_time']
                })
        else:
            print("No chapters found. Downloaded the entire video.")
        
        if chapters:
            extract_chapters(video_path, chapters)
            print(f"Chapters downloaded to the 'chapters' directory.")
    except Exception as e:
        print(f"Error: {e}")
