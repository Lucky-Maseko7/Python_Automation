import yt_dlp
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
import speech_recognition as sr
from pydub import AudioSegment
import os
import subprocess
import sys

def update_yt_dlp():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
        print("yt-dlp has been updated to the latest version.")
    except subprocess.CalledProcessError:
        print("Failed to update yt-dlp. Please update it manually using 'pip install --upgrade yt-dlp'.")

def download_video(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'temp_video.%(ext)s',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            chapters = info.get('chapters', [])
        return chapters, info['duration']
    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading video: {str(e)}")
        print("Attempting to update yt-dlp...")
        update_yt_dlp()
        print("Please run the script again after updating yt-dlp.")
        return None, None

def extract_audio(video_file):
    audio_file = "temp_audio.wav"
    video = VideoFileClip(video_file)
    video.audio.write_audiofile(audio_file)
    return audio_file

def generate_subtitles(audio_file, start_time, end_time):
    try:
        audio = AudioSegment.from_wav(audio_file)
        chunk = audio[start_time*1000:end_time*1000]
        chunk.export("temp_chunk.wav", format="wav")
        
        recognizer = sr.Recognizer()
        with sr.AudioFile("temp_chunk.wav") as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                text = "Unable to generate subtitles for this segment"
        
        os.remove("temp_chunk.wav")
        return text
    except Exception as e:
        print(f"Error generating subtitles: {str(e)}")
        return "Subtitle generation failed"

def add_subtitle_to_frame(frame, text, font_scale=1, thickness=2):
    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (w - text_size[0]) // 2
    text_y = h - 30
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
    return frame

def create_clip(video_file, start_time, end_time, subtitle_text):
    try:
        cap = cv2.VideoCapture(video_file)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('temp_output.mp4', fourcc, fps, (width, height))
        
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or cap.get(cv2.CAP_PROP_POS_MSEC) > end_time * 1000:
                break
            
            frame_with_subtitle = add_subtitle_to_frame(frame, subtitle_text)
            out.write(frame_with_subtitle)
        
        cap.release()
        out.release()
        
        # Add audio to the video
        video = VideoFileClip('temp_output.mp4')
        audio = AudioFileClip(video_file).subclip(start_time, end_time)
        final_clip = video.set_audio(audio)
        
        return final_clip
    except Exception as e:
        print(f"Error creating clip: {str(e)}")
        return None

def main(url, output_folder):
    chapters, duration = download_video(url)
    if chapters is None:
        return

    video_file = "temp_video.mp4"
    if not os.path.exists(video_file):
        print(f"Error: {video_file} not found. The download may have failed.")
        return

    audio_file = extract_audio(video_file)

    if not chapters:
        print("No chapters found. Processing the entire video as one clip...")
        chapters = [{'start_time': 0, 'end_time': duration}]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for i, chapter in enumerate(chapters):
        start_time = chapter['start_time']
        end_time = chapter.get('end_time', duration)
        
        subtitle_text = generate_subtitles(audio_file, start_time, end_time)
        clip = create_clip(video_file, start_time, end_time, subtitle_text)
        
        if clip:
            output_file = os.path.join(output_folder, f"clip_{i+1}.mp4")
            clip.write_videofile(output_file)
        else:
            print(f"Failed to create clip {i+1}")
    
    if os.path.exists(video_file):
        os.remove(video_file)
    if os.path.exists(audio_file):
        os.remove(audio_file)
    if os.path.exists('temp_output.mp4'):
        os.remove('temp_output.mp4')

if __name__ == "__main__":
    url = input("Enter a valid YouTube URL: ")
    output_folder = input("Enter the output folder name: ")
    main(url, output_folder)