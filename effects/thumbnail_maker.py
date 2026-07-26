from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

def create_thumbnail(title, background_image_url, output_path="thumbnail.jpg"):
    """Generate a thumbnail with text overlay."""
    # Download background
    response = requests.get(background_image_url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((1280, 720))  # YouTube thumbnail size
    
    # Add text
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 60)
    text_width, text_height = draw.textsize(title, font=font)
    
    # Center the text
    x = (1280 - text_width) / 2
    y = (720 - text_height) / 2
    draw.text((x, y), title, font=font, fill="white", stroke_width=2, stroke_fill="black")
    
    img.save(output_path)
    return output_path