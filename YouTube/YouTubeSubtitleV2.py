from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import re

# Set your YouTube Data API key here
API_KEY = "AIzaSyDXmsIrmsukvm--Y2URxVZfdpvljyoP3mU"

def get_video_id(url):
    # Extracts the video id from the YouTube URL
    video_id = re.search(r'(?<=v=)[^&#]+', url)
    if not video_id:
        video_id = re.search(r'(?<=be/)[^&#]+', url)
    return video_id.group(0) if video_id else None

def get_video_title(video_id):
    # Fetches the video title using YouTube Data API
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()

    title = response['items'][0]['snippet']['title']
    return sanitize_filename(title.replace(" ", "_"))

def sanitize_filename(filename):
    # Replaces invalid characters in filenames
    return re.sub(r'[\/:*?"<>|$]', '_', filename)

def fetch_transcript(video_id, language='en'):
    # Fetches the transcript for the video id
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return transcript
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def generate_srt(transcript):
    # Converts transcript to SRT format
    srt_content = ""
    for i, entry in enumerate(transcript):
        start_time = entry['start']
        duration = entry['duration']
        text = entry['text']

        start_time_str = format_time(start_time)
        end_time_str = format_time(start_time + duration)

        srt_content += f"{i + 1}\n{start_time_str} --> {end_time_str}\n{text}\n\n"

    return srt_content

def format_time(seconds):
    # Formats time in seconds to SRT time format
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

def save_srt(content, filename):
    # Saves SRT content to a file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

if __name__ == "__main__":
    youtube_url = input("Enter YouTube video URL: ")
    video_id = get_video_id(youtube_url)
    
    if video_id:
        video_title = get_video_title(video_id)
        transcript = fetch_transcript(video_id)
        
        if transcript:
            srt_content = generate_srt(transcript)
            filename = f"{video_title}.srt"
            save_srt(srt_content, filename)
            print(f"Subtitles saved as {filename}")
        else:
            print("Could not fetch transcript.")
    else:
        print("Invalid YouTube URL.")
