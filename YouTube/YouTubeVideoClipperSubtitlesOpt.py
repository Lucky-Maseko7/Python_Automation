import os
import re
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.VideoClip import ImageClip
from PIL import Image, ImageDraw, ImageFont
import speech_recognition as sr
import pysrt
from webvtt import WebVTT, Caption
from yt_dlp import YoutubeDL
import numpy as np

def get_video_url():
    while True:
        url = input("Enter the YouTube video URL: ").strip()
        if url.startswith(('https://www.youtube.com/watch?v=', 'https://youtu.be/')):
            return url
        else:
            print("Invalid YouTube URL. Please enter a valid URL starting with 'https://www.youtube.com/watch?v=' or 'https://youtu.be/'")

def download_video(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '%(title)s.%(ext)s'
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return filename, info
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None, None

def extract_chapters(info):
    try:
        chapters = info.get('chapters', [])
        if not chapters:
            return []
        
        parsed_chapters = []
        for chapter in chapters:
            parsed_chapters.append({
                'title': chapter['title'],
                'start': chapter['start_time'],
                'end': chapter['end_time']
            })
        
        return parsed_chapters
    except Exception as e:
        print(f"Error extracting chapters: {str(e)}")
        return []

def create_clip(video, start_time, end_time):
    return video.subclip(start_time, end_time)

def speech_to_text(audio_path, language='en-US'):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        print("Speech recognition could not understand the audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from speech recognition service; {str(e)}")
        return ""

def generate_captions(text, start_time, end_time, format='srt'):
    words = text.split()
    duration = end_time - start_time
    words_per_second = len(words) / duration
    
    captions = []
    current_time = start_time
    caption_text = ""
    
    for word in words:
        caption_text += word + " "
        if len(caption_text.split()) >= 7 or word == words[-1]:
            end_caption_time = current_time + len(caption_text.split()) / words_per_second
            
            if format == 'srt':
                caption = pysrt.SubRipItem(
                    index=len(captions) + 1,
                    start=pysrt.SubRipTime(seconds=current_time),
                    end=pysrt.SubRipTime(seconds=end_caption_time),
                    text=caption_text.strip()
                )
            elif format == 'vtt':
                caption = Caption(
                    start=current_time,
                    end=end_caption_time,
                    text=caption_text.strip()
                )
            
            captions.append(caption)
            current_time = end_caption_time
            caption_text = ""
    
    if format == 'srt':
        srt_file = pysrt.SubRipFile(items=captions)
        return srt_file
    elif format == 'vtt':
        vtt_file = WebVTT()
        for caption in captions:
            vtt_file.captions.append(caption)
        return vtt_file

def create_text_clip(text, size, duration, font_size=50):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arialbd.ttf", font_size)
    
    # Split the text into words
    words = text.split()
    
    # Calculate total width and height of all words
    total_width = sum(draw.textlength(word, font=font) for word in words) + (len(words) - 1) * font_size * 0.2
    _, _, _, text_height = draw.textbbox((0, 0), text, font=font)
    
    # Calculate starting position
    start_x = (size[0] - total_width) / 2
    start_y = size[1] - text_height - 10
    
    # Function to draw text with shadow and outline
    def draw_text_with_effects(word, position, color):
        # Draw shadow
        shadow_offset = (3, 3)
        draw.text((position[0] + shadow_offset[0], position[1] + shadow_offset[1]), word, font=font, fill=(0, 0, 0, 255))
        
        # Draw outline
        for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            draw.text((position[0] + offset[0], position[1] + offset[1]), word, font=font, fill=(0, 0, 0, 255))
        
        # Draw main text
        draw.text(position, word, font=font, fill=color)
    
    # Draw each word
    current_x = start_x
    for word in words:
        word_width = draw.textlength(word, font=font)
        color = (0, 255, 0, 255) if word.lower() == 'spoke' else (255, 255, 255, 255)
        draw_text_with_effects(word, (current_x, start_y), color)
        current_x += word_width + font_size * 0.2  # Add space between words
    
    return ImageClip(np.array(img)).set_duration(duration)

def add_captions_to_clip(clip, captions):
    subtitle_clips = []
    for caption in captions:
        start_time = caption.start.seconds
        end_time = caption.end.seconds
        duration = end_time - start_time
        subtitle_clip = create_text_clip(caption.text, clip.size, duration)
        subtitle_clips.append(subtitle_clip.set_start(start_time))

    final_clip = CompositeVideoClip([clip] + subtitle_clips)
    return final_clip

def main():
    url = get_video_url()
    video_path, info = download_video(url)
    
    if not video_path:
        print("Failed to download video. Exiting.")
        return
    
    video = VideoFileClip(video_path)
    chapters = extract_chapters(info)
    
    if not chapters:
        print("No chapters found. Extracting whole video.")
        chapters = [{'title': 'Full Video', 'start': 0, 'end': video.duration}]
    
    for chapter in chapters:
        clip = create_clip(video, chapter['start'], chapter['end'])
        audio_file = f"C:\\Users\\ltmas\\Videos\\RawContent\\YoutubeDownloads\\temp_audio_{chapter['start']}.wav"
        clip.audio.write_audiofile(audio_file)
        
        text = speech_to_text(audio_file)
        os.remove(audio_file)
        
        captions = generate_captions(text, 0, chapter['end'] - chapter['start'], format='srt')
        final_clip = add_captions_to_clip(clip, captions)
        
        output_filename = f"C:\\Users\\ltmas\\Videos\\RawContent\\YoutubeDownloads\\{re.sub(r'[^\w\-_\. ]', '_', chapter['title'])}.mp4"
        final_clip.write_videofile(output_filename)
        
        print(f"Created clip: {output_filename}")
    
    video.close()

if __name__ == "__main__":
    main()