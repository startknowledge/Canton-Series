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
    from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips

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
    cmd = ["ffmpeg", "-y", "-i", str(temp_video)]
    audio_paths = []
    for lang, path in audio_files.items():
        cmd.extend(["-i", str(path)])
        audio_paths.append((lang, path))

    cmd.extend(["-map", "0:v"])
    for i in range(len(audio_paths)):
        cmd.extend(["-map", f"{i+1}:a"])

    cmd.extend(["-c:v", "copy"])
    for i, (lang, _) in enumerate(audio_paths):
        cmd.extend([f"-metadata:s:a:{i}", f"language={lang}"])

    cmd.append(str(output_path))

    success = run_ffmpeg_command(cmd, "Adding multiple audio tracks")
    if success and output_path.exists():
        logger.info(f"Final video with {len(audio_paths)} audio tracks: {output_path}")
        if temp_video.exists():
            temp_video.unlink()
        return output_path
    else:
        raise RuntimeError("Failed to create multi-audio video")

# ✅ FIX: Corrected split_and_upload_shorts function
def split_and_upload_shorts(input_video: Path, uploader, title: str):
    """
    Split a video into 60-second vertical shorts and upload them.
    input_video: Path to the main video file.
    uploader: An instance of YouTubeUploader.
    title: The title of the main video.
    """
    from pathlib import Path
    import subprocess

    duration = 60  # 1 minute per short
    video_duration = 840  # 14 minutes total (adjust if your video changes)
    shorts_uploaded = []

    logger.info(f"Splitting video into shorts: {input_video}")
    
    for i in range(0, video_duration, duration):
        start_time = i
        part_num = i // duration + 1
        output_name = f"short_part_{part_num}.mp4"
        output_path = Path(TEMP_DIR / "videos" / output_name)

        # Vertical crop (1080x1920) aur 60 sec cut
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", str(input_video),
                "-vf", "crop=in_w:in_w*9/16:0:(in_h-in_w*9/16)/2",
                "-ss", str(start_time), "-t", str(duration),
                "-c:v", "libx264", "-c:a", "aac", str(output_path)
            ], check=True)
            logger.info(f"Short created: {output_path}")
            
            # Short Upload karein
            uploader.upload_video(
                video_path=output_path,
                title=f"{title[:50]} - Part {part_num} #shorts",
                privacy_status="public", # Shorts humesha public better hai
                description=f"Watch the full episode on our channel! Part {part_num} of the Canton Series."
            )
            shorts_uploaded.append(output_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate short for part {part_num}: {e}")

    logger.info(f"Uploaded {len(shorts_uploaded)} shorts.")
    return shorts_uploaded
