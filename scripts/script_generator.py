import openai
import google.generativeai as genai
from scripts.config import APIConfig, DEFAULT_TOPICS
from scripts.utils import logger

# System prompt (unchanged)
SYSTEM_PROMPT = """Act as a world-class documentary scriptwriter for a 'Canton Series'.
Your tone is cinematic, mysterious, and deeply educational.
Never use generic AI phrases. Provide timestamps and visual cues."""

def generate_script(topic, provider="openai"):
    """Generate a 14‑minute script for a given topic."""
    user_prompt = f"""Write a 14‑minute script about "{topic}".
Structure:
0:00-2:30 Hook
2:30-8:00 Deep Dive (3 acts)
8:00-10:30 Visual Spectacle (2 detailed scenes)
10:30-14:00 Outro + CTA

Format:
[SCENE: description]
NARRATOR: dialogue
..."""
    if provider == "openai":
        client = openai.OpenAI(api_key=APIConfig.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": user_prompt}],
            temperature=0.85, max_tokens=4000
        )
        return resp.choices[0].message.content
    else:
        # Gemini fallback (if you have key)
        import google.generativeai as genai
        genai.configure(api_key=APIConfig.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        resp = model.generate_content(SYSTEM_PROMPT + "\n\n" + user_prompt)
        return resp.text

def translate_script(script, target_lang_code):
    """Translate script into another language (only NARRATOR parts)."""
    prompt = f"""Translate the following YouTube script into {target_lang_code} (language code: {target_lang_code}).
Keep the exact same format: [SCENE: ...] and NARRATOR: ... lines.
Do not change the scenes, only translate the narrator dialogue.

SCRIPT:
{script}
"""
    client = openai.OpenAI(api_key=APIConfig.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "system", "content": "You are a professional translator."},
                  {"role": "user", "content": prompt}],
        temperature=0.3
    )
    return resp.choices[0].message.content

def get_next_topic(index):
    topics = DEFAULT_TOPICS
    if index >= len(topics):
        return topics[index % len(topics)], True
    return topics[index], False