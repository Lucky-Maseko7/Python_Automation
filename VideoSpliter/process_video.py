from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx.all import crop, resize

def process_video(input_url, chapters, crop_coords, text, position, font_size, color, filter_fx=None):
    # Load the video from URL
    video = VideoFileClip(input_url)
    
    for chapter in chapters:
        start_time = chapter['start_time']
        end_time = chapter['end_time']
        title = chapter['title']
        
        # Trim the video for the chapter
        trimmed_video = video.subclip(start_time, end_time)
        
        # Crop the video
        cropped_video = crop(trimmed_video, x1=crop_coords[0], y1=crop_coords[1], x2=crop_coords[2], y2=crop_coords[3])
        
        # Add text to the video
        txt_clip = TextClip(f"{text} - {title}", fontsize=font_size, color=color)
        txt_clip = txt_clip.set_position(position).set_duration(cropped_video.duration)
        video_with_text = CompositeVideoClip([cropped_video, txt_clip])
        
        # Apply filter if specified
        if filter_fx:
            final_video = filter_fx(video_with_text)
        else:
            final_video = video_with_text
        
        # Save the final video for each chapter
        output_path = f"output_{title}.mp4"
        final_video.write_videofile(output_path, codec="libx264")

# Example usage
input_url = "https://www.youtube.com/watch?v=fXZBumNTnQU"
chapters = [
    {"title": "Introduction", "start_time": 0, "end_time": 60},
    {"title": "Chapter 1", "start_time": 60, "end_time": 300},
    {"title": "Chapter 2", "start_time": 300, "end_time": 600}
]
crop_coords = (100, 100, 400, 400)  # (x1, y1, x2, y2)
text = "Chapter"
position = ("center", "top")
font_size = 50
color = "white"

# Applying a simple resize filter for demonstration
def resize_filter(clip):
    return resize(clip, 0.5)

process_video(input_url, chapters, crop_coords, text, position, font_size, color, filter_fx=resize_filter)
