import os
import yt_dlp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Function to download YouTube video
def download_video(url, output_path):
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'cookies-from-browser': 'chrome',  # Use cookies from Chrome
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return info_dict

# Function to extract chapters
def extract_chapters(video_path, chapters, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for i, chapter in enumerate(chapters):
        start_time = chapter['start_time']
        end_time = chapter.get('end_time')
        title = chapter['title'].replace(" ", "_").replace("/", "_").replace("\\", "_")
        output_path = os.path.join(output_dir, f"{i+1}_{title}.mp4")
        if end_time is None:
            end_time = video_duration
        ffmpeg_extract_subclip(video_path, start_time, end_time, targetname=output_path)

# Main script
if __name__ == "__main__":
    url = input("Enter YouTube video URL: ")
    full_video_path = 'C:\\Users\\ltmas\\Videos\\RawContent\\YouTube\\video.mp4'
    chapters_dir = 'C:\\Users\\ltmas\\Videos\\RawContent\\YouTube\\Chapters'
    
    try:
        info_dict = download_video(url, full_video_path)
        chapters = []
        video_duration = info_dict.get('duration', 0)
        
        if 'chapters' in info_dict:
            for chapter in info_dict['chapters']:
                chapters.append({
                    'title': chapter['title'],
                    'start_time': chapter['start_time'],
                    'end_time': chapter.get('end_time')
                })
        else:
            print("No chapters found. Downloaded the entire video.")
        
        if chapters:
            extract_chapters(full_video_path, chapters, chapters_dir)
            print(f"Chapters downloaded to the 'C:\\Users\\ltmas\\Videos\\RawContent\\YouTube\\Chapters' directory.")
        else:
            print("No chapters available.")
            
    except Exception as e:
        print(f"Error: {e}")
