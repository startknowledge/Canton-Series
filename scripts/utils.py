"""
Shared utility functions for Canton Studio
"""
import json, logging, os, subprocess, sys
from datetime import datetime
from pathlib import Path
from typing import List

from scripts.config import LOGS_DIR

LOG_FILE = LOGS_DIR / f"automation_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("canton-studio")

def save_json(data: Any, filepath: Path) -> None:
    """Save data as JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filepath: Path) -> Any:
    """Load data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def ensure_dir(path: Path) -> None:
    """Ensure directory exists"""
    path.mkdir(parents=True, exist_ok=True)

def run_ffmpeg_command(args: List[str], desc: str = "") -> bool:
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False
        logger.info(f"FFmpeg completed: {desc}")
        return True
    except Exception as e:
        logger.error(f"FFmpeg exception: {e}")
        return False

def get_file_size(filepath: Path) -> int:
    """Get file size in bytes"""
    return os.path.getsize(filepath) if filepath.exists() else 0

def clean_temp_files(days_old: int = 7) -> None:
    """Delete temporary files older than specified days"""
    import time
    from scripts.config import TEMP_DIR
    
    now = time.time()
    for root, dirs, files in os.walk(TEMP_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            if os.path.getmtime(filepath) < now - (days_old * 86400):
                try:
                    os.remove(filepath)
                    logger.info(f"Deleted old temp file: {filepath}")
                except Exception as e:
                    logger.warning(f"Could not delete {filepath}: {e}")