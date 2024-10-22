import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import speech_recognition as sr
import pysrt
from webvtt import WebVTT, Caption
from yt_dlp import YoutubeDL
import numpy as np
from pytube import YouTube
import tempfile
from functools import lru_cache

# Cache for font objects and image processing
@lru_cache(maxsize=128)
def get_font(font_name, size):
    return ImageFont.truetype(font_name, size)

@lru_cache(maxsize=32)
def create_subtitle_image_cached(text, width, height, font_size=50):
    videosize = (width, height)
    img = Image.new('RGBA', videosize, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = get_font("arialbd.ttf", font_size)
    
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top
    text_position = ((videosize[0] - text_width) / 2, videosize[1] - text_height - 10)
    
    bg_height = text_height + 10
    bg_top = videosize[1] - bg_height
    draw.rectangle([(0, bg_top), (videosize[0], videosize[1])], fill=(0, 0, 0, 255))
    draw.text(text_position, text, font=font, fill=(255, 255, 255, 255))
    
    return np.array(img)

def create_video_subfolder(download_path, video_url):
    """
    Creates a subfolder for the video and its clips.
    """
    try:
        yt = YouTube(video_url)
        # Clean the video title to make it filesystem-friendly
        video_title = re.sub(r'[<>:"/\\|?*]', '_', yt.title)
        video_title = video_title.replace(' ', '_')
        
        video_folder_path = os.path.join(download_path, video_title)
        clips_folder_path = os.path.join(video_folder_path, "clips")
        
        # Create folders if they don't exist
        os.makedirs(video_folder_path, exist_ok=True)
        os.makedirs(clips_folder_path, exist_ok=True)
        
        return video_folder_path, clips_folder_path
    except Exception as e:
        print(f"Error creating subfolder: {e}")
        print("Using default folder structure.")
        # Create a generic subfolder
        generic_folder = os.path.join(download_path, "youtube_video")
        generic_clips_folder = os.path.join(generic_folder, "clips")
        
        os.makedirs(generic_folder, exist_ok=True)
        os.makedirs(generic_clips_folder, exist_ok=True)
        
        return generic_folder, generic_clips_folder

def download_video(url, destination_folder):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True
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
    """
    Extracts chapter information from the video metadata.
    """
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

def process_audio_chunk(audio_chunk, recognizer, language='en-US'):
    try:
        text = recognizer.recognize_google(audio_chunk, language=language)
        return text
    except (sr.UnknownValueError, sr.RequestError):
        return ""


def extract_audio_safely(video_clip, output_path):
    """
    Safely extracts audio from a video clip with error handling.
    """
    try:
        # First try using moviepy's built-in audio extraction
        if video_clip.audio is not None:
            video_clip.audio.write_audiofile(
                output_path,
                codec='pcm_s16le',  # Use WAV format
                ffmpeg_params=['-ac', '1'],  # Convert to mono
                logger=None
            )
            return True
        else:
            print("No audio stream found in video clip")
            return False
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return False

def parallel_speech_to_text(audio_path, chunk_duration=30, language='en-US'):
    """
    Enhanced parallel speech-to-text with better error handling
    """
    if not os.path.exists(audio_path):
        print(f"Audio file not found: {audio_path}")
        return ""
        
    try:
        recognizer = sr.Recognizer()
        audio_clip = AudioFileClip(audio_path)
        total_duration = audio_clip.duration
        
        if total_duration <= 0:
            print("Invalid audio duration")
            return ""
        
        chunks = []
        for start_time in np.arange(0, total_duration, chunk_duration):
            end_time = min(start_time + chunk_duration, total_duration)
            chunk = audio_clip.subclip(start_time, end_time)
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                chunk.write_audiofile(temp_file.name, logger=None)
                chunks.append(temp_file.name)
        
        texts = []
        with ThreadPoolExecutor(max_workers=min(os.cpu_count(), 4)) as executor:
            futures = []
            for chunk_path in chunks:
                try:
                    with sr.AudioFile(chunk_path) as source:
                        audio_data = recognizer.record(source)
                        futures.append(executor.submit(process_audio_chunk, audio_data, recognizer, language))
                except Exception as e:
                    print(f"Error processing audio chunk: {e}")
                    continue
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        texts.append(result)
                except Exception as e:
                    print(f"Error getting future result: {e}")
                    continue
        
        # Cleanup temporary files
        for chunk_path in chunks:
            try:
                os.unlink(chunk_path)
            except:
                pass
        
        return " ".join(texts)
    except Exception as e:
        print(f"Error in parallel speech to text: {e}")
        return ""
    finally:
        try:
            audio_clip.close()
        except:
            pass

def process_chapter(chapter, video, clips_folder):
    """
    Enhanced chapter processing with better error handling
    """
    try:
        if not video or not video.reader:
            print("Invalid video clip")
            return None
            
        clip = video.subclip(chapter['start'], chapter['end'])
        if not clip:
            print("Failed to create subclip")
            return None
        
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            audio_path = temp_audio.name
            
        # Extract audio safely
        if not extract_audio_safely(clip, audio_path):
            print("Failed to extract audio")
            try:
                os.unlink(audio_path)
            except:
                pass
            # Continue with empty subtitles rather than failing
            text = ""
        else:
            # Process audio to text
            text = parallel_speech_to_text(audio_path)
            try:
                os.unlink(audio_path)
            except:
                pass
        
        # Generate captions (even if empty)
        captions = generate_captions(text, 0, chapter['end'] - chapter['start'], format='srt')
        final_clip = add_captions_to_clip(clip, captions)
        
        if not final_clip:
            print("Failed to create final clip")
            return None
        
        safe_title = re.sub(r'[^\w\-_\. ]', '_', chapter['title'])
        output_filename = os.path.join(clips_folder, f"{safe_title}.mp4")
        
        # Write video file with enhanced error handling
        try:
            final_clip.write_videofile(
                output_filename,
                codec='libx264',
                audio_codec='aac',
                preset='slow',
                ffmpeg_params=['-crf', '17'],
                threads=min(os.cpu_count(), 4),
                logger=None,
                verbose=False
            )
            return output_filename
        except Exception as e:
            print(f"Error writing video file: {e}")
            if os.path.exists(output_filename):
                try:
                    os.unlink(output_filename)
                except:
                    pass
            return None
            
    except Exception as e:
        print(f"Error processing chapter '{chapter['title']}': {str(e)}")
        return None
    finally:
        try:
            clip.close()
        except:
            pass
        try:
            final_clip.close()
        except:
            pass

def main():
    """
    Enhanced main function with better error handling
    """
    try:
        url = input("Enter the YouTube video URL: ").strip()
        download_path = input("Enter the destination folder path: ").strip()
        
        if not os.path.exists(download_path):
            print(f"Creating directory: {download_path}")
            os.makedirs(download_path, exist_ok=True)
        
        destination_folder, clips_folder = create_video_subfolder(download_path, url)
        video_path, info = download_video(url, destination_folder)
        
        if not video_path or not os.path.exists(video_path):
            print("Failed to download video. Exiting.")
            return
        
        try:
            video = VideoFileClip(video_path)
            if not video.reader:
                print("Failed to load video. Exiting.")
                return
                
            chapters = extract_chapters(info) or [{'title': 'Full Video', 'start': 0, 'end': video.duration}]
            
            with ThreadPoolExecutor(max_workers=min(os.cpu_count(), 2)) as executor:
                futures = [
                    executor.submit(process_chapter, chapter, video, clips_folder)
                    for chapter in chapters
                ]
                
                for future in as_completed(futures):
                    try:
                        if output_filename := future.result():
                            print(f"Created clip: {output_filename}")
                        else:
                            print("Failed to create clip")
                    except Exception as e:
                        print(f"Error processing future: {e}")
                        
        finally:
            try:
                video.close()
            except:
                pass
                
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()