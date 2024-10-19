import os
import re
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import speech_recognition as sr
import pysrt
from webvtt import WebVTT, Caption
from yt_dlp import YoutubeDL
import numpy as np
from pytube import YouTube

def get_video_url():
    while True:
        url = input("Enter the YouTube video URL: ").strip()
        if url.startswith(('https://www.youtube.com/watch?v=', 'https://youtu.be/')):
            return url
        else:
            print("Invalid YouTube URL. Please enter a valid URL starting with 'https://www.youtube.com/watch?v=' or 'https://youtu.be/'")

def download_video(url, destination_folder):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s')
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
    
    # Get the bounding box of the text
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top
    
    position = ((size[0] - text_width) / 2, size[1] - text_height - 10)
    
    # Draw the shadow (slightly offset the position for the shadow effect)
    shadow_offset = (3, 3)  # The distance of the shadow from the text
    draw.text((position[0] + shadow_offset[0], position[1] + shadow_offset[1]), 
              text, font=font, fill=(0, 0, 0, 255))  # Shadow in dark gray
    
    # Draw the text with a black outline
    for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        draw.text((position[0] + offset[0], position[1] + offset[1]), text, font=font, fill=(0, 0, 0, 255))
    
    # Draw the main text in white
    draw.text(position, text, font=font, fill=(255, 255, 255, 255))
    
    return ImageClip(np.array(img)).set_duration(duration)

def blur_frame(image, blur_radius=5):
    return np.array(Image.fromarray(image).filter(ImageFilter.GaussianBlur(blur_radius)))

def create_background(clip, target_aspect_ratio=9/16):
    target_height = int(clip.w / target_aspect_ratio)
    target_width = clip.w

    if clip.h / clip.w > target_aspect_ratio:
        background = clip.resize(width=target_width)
    else:
        background = clip.resize(height=target_height)

    x_center = background.w / 2
    y_center = background.h / 2
    background = background.crop(x1=x_center - target_width/2,
                                 y1=y_center - target_height/2,
                                 x2=x_center + target_width/2,
                                 y2=y_center + target_height/2)

    blurred_background = background.fl_image(lambda image: blur_frame(image, blur_radius=10))
    return blurred_background

def create_subtitle_image(text, videosize, font_size=24):
    # Create a new image with a transparent background
    img = Image.new('RGBA', videosize, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load a font
    font = ImageFont.truetype("arial.ttf", font_size)

    # Calculate text size and position using textbbox
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top
    text_position = ((videosize[0] - text_width) / 2, videosize[1] - text_height - 10)

    # Draw semi-transparent black background
    bg_height = text_height + 10
    bg_top = videosize[1] - bg_height
    draw.rectangle([(0, bg_top), (videosize[0], videosize[1])], fill=(0, 0, 0, 153))

    # Draw text
    draw.text(text_position, text, font=font, fill=(255, 255, 255, 255))

    return np.array(img)

def create_subtitle_clip(text, videosize, duration):
    subtitle_image = create_subtitle_image(text, videosize)
    return ImageClip(subtitle_image).set_duration(duration)

def add_captions_to_clip(clip, captions, target_aspect_ratio=9/16):
    background = create_background(clip, target_aspect_ratio)
    
    new_height = int(clip.w / target_aspect_ratio)
    new_size = (clip.w, new_height)
    
    resized_clip = clip.resize(height=clip.h)
    resized_clip = resized_clip.set_position(("center", "center"))
    
    subtitle_clips = []
    for caption in captions:
        start_time = caption.start.seconds
        end_time = caption.end.seconds
        duration = end_time - start_time
        subtitle_clip = create_subtitle_clip(caption.text, clip.size, duration)
        subtitle_clips.append(subtitle_clip.set_start(start_time))

    main_clip_with_subtitles = CompositeVideoClip([resized_clip] + subtitle_clips, size=clip.size)
    final_clip = CompositeVideoClip([background, main_clip_with_subtitles.set_position(("center", "center"))], size=new_size)
    return final_clip

def get_destination_folder():
    while True:
        folder = input("Enter the destination folder path: ").strip()
        if os.path.isdir(folder):
            return folder
        else:
            print(f"The folder '{folder}' does not exist. Please enter a valid folder path.")

# Function to create a subfolder with the full video name
def create_video_subfolder(download_path, video_url):
    try:
        yt = YouTube(video_url)
        video_title = yt.title.replace(" ", "_")  # Replace spaces with underscores to avoid directory issues
        subfolder_path = os.path.join(download_path, video_title)
        
        video_folder_path = os.path.join(download_path, video_title)
        clips_folder_path = os.path.join(video_folder_path, "clips")
        
        # Create the video folder if it doesn't exist
        if not os.path.exists(video_folder_path):
            os.makedirs(video_folder_path)
        
        # Create the clips subfolder if it doesn't exist
        if not os.path.exists(clips_folder_path):
            os.makedirs(clips_folder_path)
        
        return video_folder_path, clips_folder_path
    except Exception as e:
        print(f"Error creating subfolder: {e}")
        return download_path  # If there's an error, use the original path
    
def main():
    url = get_video_url()
    
    # Create the subfolder with the full video name
    download_path = get_destination_folder()
    destination_folder, clips_folder = create_video_subfolder(download_path, url)
    video_path, info = download_video(url, destination_folder)
    
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
        audio_file = os.path.join(clips_folder, f"temp_audio_{chapter['start']}.wav")
        clip.audio.write_audiofile(audio_file)
        
        text = speech_to_text(audio_file)
        os.remove(audio_file)
        
        captions = generate_captions(text, 0, chapter['end'] - chapter['start'], format='srt')
        final_clip = add_captions_to_clip(clip, captions)
        
        safe_title = re.sub(r'[^\w\-_\. ]', '_', chapter['title'])
        output_filename = os.path.join(clips_folder, f"{safe_title}.mp4")
        final_clip.write_videofile(output_filename)
        
        print(f"Created clip: {output_filename}")
    
    video.close()

if __name__ == "__main__":
    main()