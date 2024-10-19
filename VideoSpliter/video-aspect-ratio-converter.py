import numpy as np
import cv2
from moviepy.editor import VideoFileClip, CompositeVideoClip

def blur_frame(image, blur_amount):
    return cv2.GaussianBlur(image, (blur_amount * 2 + 1, blur_amount * 2 + 1), 0)

def convert_to_9_16_with_blurred_background(input_file, output_file, blur_amount=5):
    # Load the video file
    video = VideoFileClip(input_file)
    
    # Calculate the new dimensions
    target_aspect_ratio = 9 / 16
    original_aspect_ratio = video.w / video.h
    
    if original_aspect_ratio > target_aspect_ratio:
        # Video is wider than 9:16, expand height
        new_height = int(video.w / target_aspect_ratio)
        new_width = video.w
    else:
        # Video is taller than 9:16, expand width
        new_width = int(video.h * target_aspect_ratio)
        new_height = video.h

    # Create blurred background
    def create_background(get_frame, t):
        frame = get_frame(t)
        resized_frame = cv2.resize(frame, (new_width, new_height))
        blurred_frame = blur_frame(resized_frame, blur_amount)
        return blurred_frame

    background = video.fl(create_background)
    
    # Resize original video to fit within the new frame
    foreground = video.resize(width=video.w)  # Keep original size
    
    # Calculate position to center the original video
    position = ((new_width - foreground.w) // 2,
                (new_height - foreground.h) // 2)
    
    # Create the final composite
    final_video = CompositeVideoClip([
        background,
        foreground.set_position(position)
    ], size=(new_width, new_height))
    
    # Write the result to a file
    final_video.write_videofile(output_file, codec="libx264")
    
    # Close the video clips
    video.close()
    final_video.close()


# Usage
input_file = f"C:\\Users\\ltmas\Videos\\RawContent\\YoutubeDownloads\\Done\\Ace VTOL Slipstream Elite.mp4"
output_file = "output_video_9_16.mp4"
convert_to_9_16_with_blurred_background(input_file, output_file, blur_amount=100)
