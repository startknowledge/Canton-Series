import os
import requests
from moviepy.editor import *
from moviepy.video.fx import fadein, fadeout
from elevenlabs import generate, play, save
from pexels_api import API
import json
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
TEMP_DIR = "./temp/"
os.makedirs(TEMP_DIR, exist_ok=True)

def generate_voiceover(script_text, filename="voiceover.mp3"):
    """Generate voiceover using ElevenLabs."""
    audio = generate(
        api_key=ELEVENLABS_API_KEY,
        text=script_text,
        voice="Rachel",  # Or any other voice
        model="eleven_monolingual_v1"
    )
    save(audio, os.path.join(TEMP_DIR, filename))
    return os.path.join(TEMP_DIR, filename)

def fetch_stock_media(query, media_type="video", per_page=1):
    """Fetch royalty-free videos or images from Pexels."""
    api = API(PEXELS_API_KEY)
    if media_type == "video":
        api.search_videos(query, per_page=per_page)
        videos = api.get_videos()
        if videos:
            # Download the first video
            video_url = videos[0].video_files[0].link
            response = requests.get(video_url)
            filename = f"stock_{query.replace(' ', '_')}.mp4"
            filepath = os.path.join(TEMP_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath
    # Similar logic for images
    return None

def assemble_video(voiceover_path, media_paths, output_path="final_video.mp4"):
    """Combine voiceover and media into a final video."""
    # Load audio
    audio_clip = AudioFileClip(voiceover_path)
    
    # Load media clips (images or videos)
    clips = []
    for path in media_paths:
        if path.endswith(('.mp4', '.mov')):
            clip = VideoFileClip(path)
        else:  # Assume image
            clip = ImageClip(path).set_duration(audio_clip.duration / len(media_paths))
        clips.append(clip)
    
    # Concatenate clips
    video_clip = concatenate_videoclips(clips, method="compose")
    
    # Set the audio
    final_clip = video_clip.set_audio(audio_clip)
    
    # Write the final video
    final_clip.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    return output_path

if __name__ == "__main__":
    # Example usage - this will be called by n8n with arguments
    import sys
    script_text = sys.argv[1]  # Pass the script as an argument
    voiceover_file = generate_voiceover(script_text)
    
    # In a real scenario, you'd parse the script to extract search queries
    media_files = [fetch_stock_media("canton history"), fetch_stock_media("ancient china")]
    final_video = assemble_video(voiceover_file, media_files)
    print(final_video)  # Output the path for n8n to pick up