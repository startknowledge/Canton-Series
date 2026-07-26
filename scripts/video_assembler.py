import subprocess
from pathlib import Path
from scripts.config import TEMP_DIR, VideoConfig
from scripts.utils import logger, run_ffmpeg_command

def assemble_video_with_multiaudio(
    media_paths: list,
    audio_files: dict,   # {lang_code: Path}
    output_filename="final_video.mp4",
    add_intro=True,
    add_outro=False
) -> Path:
    """
    Combine media (images/videos) into a slideshow, then add multiple audio tracks.
    audio_files: dict of language code -> path to MP3.
    Returns Path to final MP4 with multiple audio streams.
    """
    out_dir = TEMP_DIR / "videos"
    out_dir.mkdir(exist_ok=True)
    output_path = out_dir / output_filename

    # Step 1: Create a video without audio using FFmpeg (slideshow from images/videos)
    # For simplicity, we'll use a Python script to create a slideshow with moviepy,
    # then we'll add audio tracks with FFmpeg.
    # Here we assume we already have a video file (without audio) or we build one.
    # We'll use moviepy to create a video clip from media, but we need to separate audio.
    # Approach: create a video with a silent audio track, then overlay multiple audio streams.
    from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips, CompositeVideoClip

    # Build list of clips from media paths
    clips = []
    for p in media_paths:
        if p.suffix in ['.mp4', '.mov', '.avi']:
            clip = VideoFileClip(str(p))
            clips.append(clip)
        else:  # image
            # Determine duration per image (total duration from first audio)
            total_dur = 0
            for ap in audio_files.values():
                from moviepy.editor import AudioFileClip
                dur = AudioFileClip(str(ap)).duration
                if dur > total_dur:
                    total_dur = dur
            per_image = total_dur / max(1, len([p for p in media_paths if p.suffix not in ['.mp4','.mov','.avi']]))
            clip = ImageClip(str(p)).set_duration(per_image)
            clips.append(clip)

    # Concatenate
    video_clip = concatenate_videoclips(clips, method="compose")
    video_clip = video_clip.resize(VideoConfig.RESOLUTION)

    # Write temporary video without audio
    temp_video = out_dir / "temp_video_noaudio.mp4"
    video_clip.write_videofile(str(temp_video), fps=VideoConfig.FPS, codec=VideoConfig.VIDEO_CODEC, audio_codec=None, verbose=False, logger=None)

    # Step 2: Use FFmpeg to add multiple audio streams
    # Build command: -i video -i audio1 -i audio2 ... -map 0:v -map 1:a -map 2:a ... -c copy -metadata:s:a:0 language=eng ...
    cmd = ["ffmpeg", "-y", "-i", str(temp_video)]
    audio_paths = []
    for lang, path in audio_files.items():
        cmd.extend(["-i", str(path)])
        audio_paths.append((lang, path))

    # Map video
    cmd.extend(["-map", "0:v"])
    # Map each audio
    for i in range(len(audio_paths)):
        cmd.extend(["-map", f"{i+1}:a"])

    # Set codec copy for video, encode audio with aac
    cmd.extend(["-c:v", "copy"])
    # For each audio stream, set language metadata
    for i, (lang, _) in enumerate(audio_paths):
        cmd.extend([f"-metadata:s:a:{i}", f"language={lang}"])

    cmd.append(str(output_path))

    success = run_ffmpeg_command(cmd, "Adding multiple audio tracks")
    if success and output_path.exists():
        logger.info(f"Final video with {len(audio_paths)} audio tracks: {output_path}")
        # Clean up temp
        if temp_video.exists():
            temp_video.unlink()
        return output_path
    else:
        raise RuntimeError("Failed to create multi-audio video")