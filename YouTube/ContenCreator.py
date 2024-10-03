import moviepy.editor as mp
import speech_recognition as sr
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.VideoClip import TextClip

def extract_audio_from_video(video_file):
    """Extracts audio from a video file."""
    video = mp.VideoFileClip(video_file)
    audio_file = "audio.wav"
    video.audio.write_audiofile(audio_file)
    return audio_file

def audio_to_text(audio_file):
    """Converts audio to text using speech recognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        # Using Google Web Speech API (can be replaced with other APIs)
        try:
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "[Unintelligible]"
        except sr.RequestError as e:
            return f"Could not request results; {e}"

def generate_subtitles(video_file, subtitle_text, font='Arial', font_size=24, font_color='white'):
    """Overlay subtitles on a video file with customizable style."""
    # Define the video and subtitle style
    video = mp.VideoFileClip(video_file)
    
    # Create a function that generates subtitle TextClip for each time interval
    def subtitle_generator(txt):
        return TextClip(txt, fontsize=font_size, font=font, color=font_color)
    
    # Assuming you have subtitle text divided per second (for simplicity here)
    # You would need timestamps in a real scenario
    subs = [(i, subtitle_text) for i in range(int(video.duration))]
    
    subtitles = SubtitlesClip(subs, subtitle_generator)
    
    # Overlay subtitles on the video
    result = mp.CompositeVideoClip([video, subtitles.set_position(('center', 'bottom'))])
    
    # Write the output video with subtitles
    result.write_videofile(f"{video_file.split('.')[0]}_with_subtitles.mp4", fps=video.fps)

if __name__ == "__main__":
    video_file = "C:\\Users\\ltmas\\Videos\\RawContent\\YouTube\\video.mp4"  # Replace with actual video file path
    audio_file = extract_audio_from_video(video_file)
    subtitle_text = audio_to_text(audio_file)
    
    # Customize subtitle style (font, size, color)
    generate_subtitles(video_file, subtitle_text, font='Arial', font_size=30, font_color='yellow')
