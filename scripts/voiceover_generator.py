from elevenlabs import generate, save, set_api_key, VoiceSettings
from scripts.config import APIConfig, TEMP_DIR, AUDIO_LANGUAGES
from scripts.utils import logger

set_api_key(APIConfig.ELEVENLABS_API_KEY)

def get_voice(lang_code):
    for lang in AUDIO_LANGUAGES:
        if lang["code"] == lang_code:
            return lang["voice"]
    return "Rachel"

def generate_voiceover(script_text, language="en", filename=None):
    voice = get_voice(language)
    if not filename:
        filename = f"voiceover_{language}.mp3"
    audio = generate(
        text=script_text,
        voice=voice,
        model="eleven_monolingual_v1",
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
    )
    out_path = TEMP_DIR / "audio" / filename
    save(audio, str(out_path))
    logger.info(f"Voiceover saved: {out_path}")
    return out_path