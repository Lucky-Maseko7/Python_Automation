import cv2
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import time

# Constants
FONT_PATH = 'C:\\Windows\\Fonts\\BRITANIC.TTF'  # Update this to the path of your font
FONT_SIZE = 24
HIGHLIGHT_COLOR = (0, 255, 0)  # Green for spoken words
DEFAULT_COLOR = (255, 255, 255)  # White for unspoken words

def load_font(font_path, font_size):
    try:
        return ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font not found at {font_path}, using default font.")
        return ImageFont.load_default()

def add_subtitle_to_frame(frame, subtitle_text, start_time, current_time, end_time):
    # Convert frame to PIL image for custom font rendering
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(frame_pil)

    # Load custom or fallback font
    font = load_font(FONT_PATH, FONT_SIZE)

    # Ensure subtitle text is uppercase
    subtitle_text = subtitle_text.upper()

    # Split the subtitle into words
    words = subtitle_text.split()
    total_words = len(words)

    # Calculate spoken words based on the elapsed time
    elapsed_time = current_time - start_time
    total_time = end_time - start_time
    spoken_words_count = int((elapsed_time / total_time) * total_words)

    # Ensure we don't go beyond the total number of words
    spoken_words_count = min(spoken_words_count, total_words)

    spoken_text = " ".join(words[:spoken_words_count])
    remaining_text = " ".join(words[spoken_words_count:])
    
    # Set text color: green for spoken words, white for remaining
    spoken_color = HIGHLIGHT_COLOR  # Green
    remaining_color = DEFAULT_COLOR  # White

    # Calculate position for the text
    w, h = frame_pil.size
    text_y = h - 50

    # Draw spoken words in green
    draw.text((20, text_y), spoken_text, font=font, fill=spoken_color)

    # Get the bounding box of the spoken text to position the remaining text
    text_bbox_spoken = draw.textbbox((20, text_y), spoken_text, font=font)
    spoken_text_width = text_bbox_spoken[2] - text_bbox_spoken[0]  # Width of the spoken text

    # Draw remaining words in white
    draw.text((20 + spoken_text_width + 10, text_y), remaining_text, font=font, fill=remaining_color)

    # Convert back to OpenCV image
    frame_with_subtitle = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
    return frame_with_subtitle

def create_clip(video_file, start_time, end_time, subtitle_text):
    try:
        cap = cv2.VideoCapture(video_file)
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('temp_output.mp4', fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

        while cap.get(cv2.CAP_PROP_POS_MSEC) < end_time * 1000:
            ret, frame = cap.read()
            if not ret:
                break

            # Get the current timestamp in the video
            current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

            # Sync subtitle words with current time
            frame_with_subtitle = add_subtitle_to_frame(frame, subtitle_text, start_time, current_time, end_time)
            out.write(frame_with_subtitle)

        cap.release()
        out.release()

        # Ensure file is written before proceeding
        time.sleep(2)

        # Check if the file exists and has content
        if not os.path.exists('temp_output.mp4') or os.path.getsize('temp_output.mp4') == 0:
            raise Exception("Failed to create temp_output.mp4 or file is empty.")

        # Add audio to the video
        video = VideoFileClip('temp_output.mp4')
        audio = AudioFileClip(video_file).subclip(start_time, end_time)
        final_clip = video.set_audio(audio)

        return final_clip
    except Exception as e:
        print(f"Error creating clip: {str(e)}")
        return None

def generate_subtitles(video_file, subtitle_data):
    clips = []
    for subtitle in subtitle_data:
        start_time, end_time, subtitle_text = subtitle
        print(f"Generating clip for subtitle: {subtitle_text}")
        clip = create_clip(video_file, start_time, end_time, subtitle_text)
        if clip:
            clips.append(clip)
        else:
            print(f"Failed to create clip for subtitle: {subtitle_text}")

    # Concatenate all clips into one video
    if clips:
        final_video = concatenate_videoclips(clips)
        final_video.write_videofile("output_with_subtitles.mp4", codec="libx264", audio_codec="aac")
        print("Video with subtitles created successfully!")
    else:
        print("No clips were generated.")

# Example usage:
subtitle_data = [
    (0, 5, "This is the first subtitle."),
    (6, 10, "Here is the second subtitle."),
    (11, 15, "The final subtitle goes here.")
]

video_file = "input_video.mp4"  # Replace with the actual path to your video
generate_subtitles(video_file, subtitle_data)
