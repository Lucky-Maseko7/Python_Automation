from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import re
import os

# Set your YouTube Data API key here
API_KEY = "AIzaSyDXmsIrmsukvm--Y2URxVZfdpvljyoP3mU"

# Set the folder path where you want to save the transcript
folder_path = r"C:\Users\ltmas\Documents\Resource\YouTube Subtitles"

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

def generate_text(transcript):
    # Converts transcript into nicely formatted plain text
    text_content = ""
    for entry in transcript:
        text_content += entry['text'] + " "
    return text_content.strip()

def save_text(content, filename, folder_path):
    # Ensures the folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Create the full file path
    full_path = os.path.join(folder_path, filename)

    # Saves content to a text file
    with open(full_path, "w", encoding="utf-8") as file:
        file.write(content)

if __name__ == "__main__":
    youtube_url = input("Enter YouTube video URL: ")
    video_id = get_video_id(youtube_url)
    
    if video_id:
        video_title = get_video_title(video_id)
        transcript = fetch_transcript(video_id)
        
        if transcript:
            text_content = generate_text(transcript)
            filename = f"{video_title}.txt"
            save_text(text_content, filename, folder_path)
            print(f"Transcript saved as {filename} in {folder_path}")
        else:
            print("Could not fetch transcript.")
    else:
        print("Invalid YouTube URL.")