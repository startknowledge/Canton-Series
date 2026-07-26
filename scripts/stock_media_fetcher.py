from pexels_api import API
from scripts.config import APIConfig, TEMP_DIR
from scripts.utils import logger
import requests

class PexelsMediaFetcher:
    def __init__(self):
        self.api = API(APIConfig.PEXELS_API_KEY)
        self.media_dir = TEMP_DIR / "media"
        self.media_dir.mkdir(exist_ok=True)

    def search_videos(self, query, per_page=5):
        self.api.search_videos(query, per_page=per_page, orientation="landscape")
        videos = self.api.get_videos()
        return [{"url": v.video_files[0].link, "id": v.id} for v in videos]

    def search_images(self, query, per_page=5):
        self.api.search_photos(query, per_page=per_page, orientation="landscape")
        photos = self.api.get_photos()
        return [{"url": p.src.get("original") or p.src.get("large"), "id": p.id} for p in photos]

    def download_media(self, url, filename=None, subdir=""):
        if not filename:
            filename = f"media_{hash(url)}.mp4"
        out_dir = self.media_dir / subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        filepath = out_dir / filename
        headers = {'User-Agent': 'Mozilla/5.0', 'Authorization': APIConfig.PEXELS_API_KEY}
        resp = requests.get(url, headers=headers, stream=True, timeout=60)
        resp.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        logger.info(f"Downloaded: {filepath}")
        return filepath

    def fetch_and_download(self, query, media_type="video", count=3, subdir=""):
        if media_type == "video":
            results = self.search_videos(query, per_page=count)
        else:
            results = self.search_images(query, per_page=count)
        downloaded = []
        for item in results:
            ext = ".mp4" if media_type == "video" else ".jpg"
            fname = f"{media_type}_{item['id']}{ext}"
            path = self.download_media(item['url'], fname, subdir)
            if path:
                downloaded.append(path)
        return downloaded