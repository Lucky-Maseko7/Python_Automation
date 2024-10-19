import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.silence import split_on_silence

def video_to_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def transcribe_audio(audio_path):
    r = sr.Recognizer()
    
    sound = AudioSegment.from_wav(audio_path)
    chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=sound.dBFS-14)
    
    whole_text = []
    for i, audio_chunk in enumerate(chunks):
        chunk_filename = f"chunk{i}.wav"
        audio_chunk.export(chunk_filename, format="wav")
        with sr.AudioFile(chunk_filename) as source:
            audio = r.record(source)
        try:
            text = r.recognize_google(audio)
        except sr.UnknownValueError as e:
            print("Error:", str(e))
        else:
            text = f"{text.capitalize()}. "
            print(chunk_filename, ":", text)
            whole_text.append(text)
        os.remove(chunk_filename)
    return whole_text

def generate_srt(transcript, video_duration):
    srt_content = ""
    char_per_second = 20
    current_time = 0
    
    for i, text in enumerate(transcript):
        start_time = current_time
        end_time = start_time + (len(text) / char_per_second)
        
        if end_time > video_duration:
            end_time = video_duration
        
        srt_content += f"{i+1}\n"
        srt_content += f"{format_time(start_time)} --> {format_time(end_time)}\n"
        srt_content += f"{text}\n\n"
        
        current_time = end_time
    
    return srt_content

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def main():
    video_path = input("Enter the path to your video file: ")
    audio_path = "temp_audio.wav"
    srt_path = "output_subtitles.srt"
    
    print("Converting video to audio...")
    video_to_audio(video_path, audio_path)
    
    print("Transcribing audio...")
    transcript = transcribe_audio(audio_path)
    
    print("Generating SRT file...")
    video = VideoFileClip(video_path)
    srt_content = generate_srt(transcript, video.duration)
    
    with open(srt_path, "w") as srt_file:
        srt_file.write(srt_content)
    
    print(f"Subtitles have been generated and saved to {srt_path}")
    
    # Clean up temporary files
    os.remove(audio_path)

if __name__ == "__main__":
    main()