import os
import re
import random
import math
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from ERAVIBES import app
from config import YOUTUBE_IMG_URL

# Preload fonts for efficiency
arial = ImageFont.truetype("ERAVIBES/assets/font2.ttf", 30)
font = ImageFont.truetype("ERAVIBES/assets/font.ttf", 30)
title_font = ImageFont.truetype("ERAVIBES/assets/font3.ttf", 45)

def resize_image(max_width, max_height, image):
    """Resize image to fit within specified dimensions while maintaining aspect ratio."""
    width_ratio = max_width / image.size[0]
    height_ratio = max_height / image.size[1]
    new_width = int(width_ratio * image.size[0])
    new_height = int(height_ratio * image.size[1])
    return image.resize((new_width, new_height))

def truncate_text(text):
    """Split text into two lines, each with a maximum of 30 characters."""
    words = text.split()
    text1, text2 = "", ""
    for word in words:
        if len(text1) + len(word) < 30:
            text1 += " " + word
        elif len(text2) + len(word) < 30:
            text2 += " " + word
    return [text1.strip(), text2.strip()]

def generate_random_color():
    """Generate a random light color."""
    return (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))

def create_neon_circle(image, center, radius, border_width, steps=30):
    """Create a neon circle effect on the image."""
    draw = ImageDraw.Draw(image)
    for step in range(steps):
        red = int((math.sin(step / steps * math.pi * 2) * 127) + 128)
        green = int((math.sin((step / steps * math.pi * 2) + (math.pi / 3)) * 127) + 128)
        blue = int((math.sin((step / steps * math.pi * 2) + (math.pi * 2 / 3)) * 127) + 128)
        draw.ellipse([
            center[0] - radius - border_width + step,
            center[1] - radius - border_width + step,
            center[0] + radius + border_width - step,
            center[1] + radius + border_width - step
        ], outline=(red, green, blue), width=border_width)
    return image

def crop_circle(img, output_size, border, crop_scale=1.5):
    """Crop the center of the image into a circle with a neon border."""
    half_width, half_height = img.size[0] / 2, img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop((
        half_width - larger_size / 2,
        half_height - larger_size / 2,
        half_width + larger_size / 2,
        half_height + larger_size / 2
    ))
    img = img.resize((output_size - 2 * border, output_size - 2 * border))
    final_img = Image.new("RGBA", (output_size, output_size), "white")
    mask_main = Image.new("L", (output_size - 2 * border, output_size - 2 * border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2 * border, output_size - 2 * border), fill=255)
    final_img.paste(img, (border, border), mask_main)
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    center = (output_size // 2, output_size // 2)
    radius = (output_size - 2 * border) // 2
    return create_neon_circle(result, center, radius, 10)

async def fetch_thumbnail(videoid):
    """Fetch and process YouTube thumbnail with neon effects and text overlays."""
    cache_path = f"cache/{videoid}_v4.png"
    if os.path.isfile(cache_path):
        return cache_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = await VideosSearch(url, limit=1).next()
        if not results or not results.get("result"):
            return YOUTUBE_IMG_URL
        result = results["result"][0]
    except Exception as e:
        print(f"Error fetching YouTube results: {e}")
        return YOUTUBE_IMG_URL

    title = re.sub(r"\W+", " ", result.get("title", "Unsupported Title")).title()
    duration = result.get("duration", "Unknown Mins")
    thumbnail_url = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0] or YOUTUBE_IMG_URL
    views = result.get("viewCount", {}).get("short", "Unknown Views")
    channel = result.get("channel", {}).get("name", "Unknown Channel")

    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail_url) as resp:
            if resp.status == 200:
                async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                    await f.write(await resp.read())

    try:
        youtube = Image.open(f"cache/thumb{videoid}.png")
        image = resize_image(1280, 720, youtube).convert("RGBA")
        background = image.filter(filter=ImageFilter.BoxBlur(20))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)
        draw = ImageDraw.Draw(background)

        circle_thumbnail = crop_circle(youtube, 400, 20).resize((400, 400))
        background.paste(circle_thumbnail, (120, 160), circle_thumbnail)

        title_lines = truncate_text(title)
        draw.text((565, 180), title_lines[0], fill=(255, 255, 255), font=title_font)
        draw.text((565, 230), title_lines[1], fill=(255, 255, 255), font=title_font)
        draw.text((565, 320), f"{channel} | {views[:23]}", (255, 255, 255), font=arial)
        draw.text((10, 10), "ERA VIBES", fill="yellow", font=font)

        line_length = 580
        red_length = int(line_length * 0.6)
        draw.line([(565, 380), (565 + red_length, 380)], fill="red", width=9)
        draw.line([(565 + red_length, 380), (565 + line_length, 380)], fill="white", width=8)
        draw.ellipse([565 + red_length - 10, 380 - 10, 565 + red_length + 10, 380 + 10], fill="red")
        draw.text((565, 400), "00:00", (255, 255, 255), font=arial)
        draw.text((1080, 400), duration, (255, 255, 255), font=arial)

        play_icons = Image.open("ERAVIBES/assets/play_icons.png").resize((580, 62))
        background.paste(play_icons, (565, 450), play_icons)

        stroke_width = 15
        stroke_color = generate_random_color()
        stroke_image = Image.new("RGBA", (1280 + 2 * stroke_width, 720 + 2 * stroke_width), stroke_color)
        stroke_image.paste(background, (stroke_width, stroke_width))

        os.remove(f"cache/thumb{videoid}.png")
        stroke_image.save(cache_path)
        return cache_path
    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        return YOUTUBE_IMG_URL
