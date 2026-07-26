import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------- Paths ----------
BASE_DIR = Path(__file__).parent.parent
TEMP_DIR = BASE_DIR / "temp"
TEMPLATES_DIR = BASE_DIR / "templates"
LOGS_DIR = BASE_DIR / "logs"

for d in [TEMP_DIR, TEMP_DIR/"scripts", TEMP_DIR/"audio", TEMP_DIR/"media",
          TEMP_DIR/"videos", TEMP_DIR/"thumbnails", LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------- API Keys ----------
class APIConfig:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
    YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ---------- 100+ Topics ----------
DEFAULT_TOPICS = [
    # Core Canton (10)
    "The Silk Road and Canton's Trade Empire",
    "Dim Sum: A Culinary History of Guangzhou",
    "The Canton System: China's Gateway to the World",
    "Martial Arts of Guangdong: Wing Chun Origins",
    "The Thirteen Factories: Canton's Foreign Quarter",
    "Canton's Opium Wars: A Turning Point in History",
    "The Pearl River: Lifeline of Southern China",
    "Guangzhou's Modern Transformation: From Factory to Tech Hub",
    "Cantonese Opera: A Dying Art Form",
    "The Canton Fair: China's Oldest Trade Exhibition",
    # History (10)
    "History of Guangzhou",
    "Ancient Canton Before the Han Dynasty",
    "Guangzhou During the Tang Dynasty",
    "The Song Dynasty and Canton Trade",
    "Ming Dynasty Guangzhou",
    "Qing Dynasty Canton",
    "European Merchants in Canton",
    "Portuguese Influence in Guangzhou",
    "British Trade in Canton",
    "The Rise of Hong Merchants",
    # Economy & Travel (10)
    "The Pearl River Delta Economy",
    "Top Attractions in Guangzhou",
    "Best Museums in Guangzhou",
    "Guangzhou Tower Guide",
    "Temple of the Six Banyan Trees",
    "Chen Clan Ancestral Hall",
    "Shamian Island History",
    "Baiyun Mountain Travel Guide",
    "Yuexiu Park Attractions",
    "Sun Yat-sen Memorial Hall",
    # Cuisine (10)
    "Cantonese Cuisine Around the World",
    "Traditional Cantonese Breakfast",
    "Best Cantonese Seafood Dishes",
    "History of Roast Goose",
    "Char Siu: Origins and Recipe",
    "Cantonese Mooncakes",
    "Wonton Noodles History",
    "Rice Noodle Rolls Explained",
    "Chinese Tea Culture in Guangdong",
    "Traditional Herbal Soups",
    # Language & Culture (10)
    "Cantonese Language Basics",
    "Learning Cantonese for Beginners",
    "Differences Between Cantonese and Mandarin",
    "Popular Cantonese Expressions",
    "Cantonese Slang Guide",
    "Traditional Chinese Characters in Guangdong",
    "Cantonese Music History",
    "Famous Cantonese Singers",
    "Cantonese Cinema Evolution",
    "Hong Kong and Cantonese Culture",
    # Festivals & Traditions (10)
    "Guangdong Folk Festivals",
    "Chinese New Year in Guangzhou",
    "Lantern Festival Traditions",
    "Dragon Boat Festival in Guangdong",
    "Mid-Autumn Festival Customs",
    "Lion Dance Traditions",
    "Dragon Dance History",
    "Temple Fairs in Guangzhou",
    "Traditional Cantonese Weddings",
    "Family Traditions in Guangdong",
    # Living & Transport (10)
    "Guangzhou Metro Guide",
    "Transportation in Guangzhou",
    "Living in Guangzhou",
    "Cost of Living in Guangzhou",
    "Studying in Guangzhou",
    "Top Universities in Guangzhou",
    "Business Opportunities in Guangzhou",
    "Startup Ecosystem of Guangzhou",
    "Technology Companies in Guangzhou",
    "Manufacturing Industry in Guangdong",
    # Business & Trade (10)
    "Import and Export Business in Guangzhou",
    "How the Canton Fair Works",
    "Sourcing Products from China",
    "Wholesale Markets in Guangzhou",
    "Electronics Markets in Guangzhou",
    "Textile Markets in Guangzhou",
    "Furniture Markets in Foshan",
    "Toy Manufacturing in Guangdong",
    "Automobile Industry in Guangzhou",
    "High-Speed Rail in Guangdong",
    # Nature & Environment (10)
    "Climate of Guangzhou",
    "Best Time to Visit Guangzhou",
    "Rainy Season in Guangdong",
    "Pearl River Night Cruise",
    "Top Parks in Guangzhou",
    "Wildlife Around the Pearl River",
    "Urban Development of Guangzhou",
    "Smart City Projects in Guangzhou",
    "Green Energy in Guangdong",
    "Environmental Protection Efforts",
    # Famous People (10)
    "Famous People from Guangdong",
    "Sun Yat-sen and Guangdong",
    "Bruce Lee's Cantonese Heritage",
    "Ip Man and Wing Chun",
    "Modern Entrepreneurs from Guangzhou",
    "Guangdong's Olympic Athletes",
    "Artists from Guangdong",
    "Traditional Crafts of Guangdong",
    "Ceramics of Guangdong",
    "Canton Porcelain History",
    # Architecture & Nightlife (10)
    "Architecture of Guangzhou",
    "Ancient Temples of Guangdong",
    "Colonial Buildings in Shamian",
    "Modern Skyscrapers of Guangzhou",
    "Bridges Across the Pearl River",
    "Nightlife in Guangzhou",
    "Shopping Streets in Guangzhou",
    "Luxury Shopping in Tianhe District",
    "Street Food in Guangzhou",
    "Future Development of the Greater Bay Area"
]   # 120+ topics

# ---------- Languages for audio tracks ----------
# YouTube supports these language codes for audio tracks.
AUDIO_LANGUAGES = [
    {"code": "en", "name": "English", "voice": "Rachel"},
    {"code": "hi", "name": "Hindi", "voice": "Adam"},
    {"code": "es", "name": "Spanish", "voice": "Carmen"},
    {"code": "fr", "name": "French", "voice": "Alice"},
    {"code": "de", "name": "German", "voice": "Anna"},
    {"code": "zh", "name": "Chinese (Mandarin)", "voice": "Xiaoxuan"},
    {"code": "ja", "name": "Japanese", "voice": "Mizuki"},
    {"code": "ar", "name": "Arabic", "voice": "Aisha"}
]

# ---------- Video Settings ----------
class VideoConfig:
    RESOLUTION = (1920, 1080)
    FPS = 30
    VIDEO_CODEC = "libx264"
    AUDIO_CODEC = "aac"
    AUDIO_BITRATE = "192k"
    DEFAULT_DURATION = 840  # 14 minutes