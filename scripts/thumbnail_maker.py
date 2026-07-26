"""
Thumbnail Generator for YouTube videos
Creates eye-catching thumbnails with text overlay
"""
import os
import requests
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

from scripts.config import TEMP_DIR
from scripts.utils import logger

class ThumbnailMaker:
    """Generate YouTube thumbnails"""
    
    def __init__(self):
        self.thumbnail_dir = TEMP_DIR / "thumbnails"
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        self.size = (1280, 720)  # YouTube thumbnail size
        
        # Try to load a font
        self.font_path = self._find_font()
    
    def _find_font(self) -> str:
        """Find a suitable font on the system"""
        font_candidates = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
        
        for font in font_candidates:
            if os.path.exists(font):
                return font
        
        # Fallback to default
        return None
    
    def download_background(self, url: str) -> Optional[Image.Image]:
        """Download background image from URL"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; CantonStudio/1.0)'}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content))
            return img
            
        except Exception as e:
            logger.error(f"Failed to download background: {str(e)}")
            return None
    
    def create_thumbnail(
        self,
        title: str,
        background: Optional[Image.Image] = None,
        background_url: Optional[str] = None,
        output_filename: str = "thumbnail.jpg",
        text_color: Tuple[int, int, int] = (255, 255, 255),
        outline_color: Tuple[int, int, int] = (0, 0, 0),
        add_gradient: bool = True
    ) -> Path:
        """
        Create a YouTube thumbnail
        
        Args:
            title: Video title (will be truncated)
            background: PIL Image object
            background_url: URL to download background
            output_filename: Output filename
            text_color: RGB tuple for text
            outline_color: RGB tuple for text outline
            add_gradient: Whether to add gradient overlay
        
        Returns:
            Path to the generated thumbnail
        """
        logger.info(f"Creating thumbnail for: {title[:50]}...")
        
        # Load background
        if background is None and background_url:
            background = self.download_background(background_url)
        
        if background is None:
            # Create a gradient background
            background = self._create_gradient_background()
        
        # Resize to YouTube thumbnail size
        background = background.resize(self.size, Image.Resampling.LANCZOS)
        
        # Add gradient overlay for better text readability
        if add_gradient:
            background = self._add_gradient_overlay(background)
        
        # Add text
        draw = ImageDraw.Draw(background)
        
        # Truncate title
        max_chars = 60
        if len(title) > max_chars:
            title = title[:max_chars - 3] + "..."
        
        # Try to use custom font, fallback to default
        try:
            font_size = 60
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (center-bottom)
        text_bbox = draw.textbbox((0, 0), title, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (self.size[0] - text_width) // 2
        y = self.size[1] - text_height - 80
        
        # Draw text with outline for better visibility
        outline_width = 3
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text(
                        (x + dx, y + dy),
                        title,
                        font=font,
                        fill=outline_color
                    )
        
        # Draw main text
        draw.text((x, y), title, font=font, fill=text_color)
        
        # Save thumbnail
        output_path = self.thumbnail_dir / output_filename
        background.save(output_path, "JPEG", quality=95)
        
        logger.info(f"Thumbnail saved: {output_path}")
        return output_path
    
    def _create_gradient_background(self) -> Image.Image:
        """Create a gradient background as fallback"""
        img = Image.new("RGB", self.size)
        draw = ImageDraw.Draw(img)
        
        # Create a gradient from dark blue to dark teal
        for y in range(self.size[1]):
            ratio = y / self.size[1]
            r = int(10 + 20 * ratio)
            g = int(20 + 30 * ratio)
            b = int(80 + 50 * ratio)
            draw.line([(0, y), (self.size[0], y)], fill=(r, g, b))
        
        return img
    
    def _add_gradient_overlay(self, img: Image.Image) -> Image.Image:
        """Add a gradient overlay for better text readability"""
        overlay = Image.new("RGBA", self.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Draw a semi-transparent gradient from bottom
        for y in range(self.size[1]):
            alpha = int(150 * (1 - y / self.size[1]))
            draw.line([(0, y), (self.size[0], y)], fill=(0, 0, 0, alpha))
        
        # Composite overlay
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        img = img.convert("RGB")
        
        return img
    
    def create_thumbnail_with_ai_prompt(
        self,
        prompt: str,
        title: str,
        output_filename: str = "thumbnail_ai.jpg"
    ) -> Path:
        """
        Create thumbnail using AI image generation (DALL-E or similar)
        This is a placeholder - you'll need to integrate with an AI image API
        """
        logger.info(f"Creating AI thumbnail with prompt: {prompt[:100]}...")
        
        # TODO: Integrate with DALL-E, Stable Diffusion, or similar
        # For now, create a fallback thumbnail
        return self.create_thumbnail(title, output_filename=output_filename)

# For testing
if __name__ == "__main__":
    maker = ThumbnailMaker()
    thumb = maker.create_thumbnail(
        "The Silk Road and Canton's Trade Empire | History Documentary",
        background_url="https://images.pexels.com/photos/.../pexels-photo.jpg"
    )
    print(f"Thumbnail created: {thumb}")