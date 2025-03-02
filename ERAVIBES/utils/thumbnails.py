import os
import re
import math
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

# Global font definitions (avoid repeated disk access)
ARIAL_FONT = ImageFont.truetype("ERAVIBES/assets/font2.ttf", 30)
TITLE_FONT = ImageFont.truetype("ERAVIBES/assets/font3.ttf", 45)


def change_image_size(max_width: int, max_height: int, image: Image.Image) -> Image.Image:
    # Resize image while maintaining aspect ratio
    width_ratio = max_width / image.size[0]
    height_ratio = max_height / image.size[1]
    new_width = int(width_ratio * image.size[0])
    new_height = int(height_ratio * image.size[1])
    return image.resize((new_width, new_height))


def truncate(text: str) -> list:
    # Split text into two lines, each with roughly 30 characters
    words = text.split(" ")
    line1, line2 = "", ""
    for word in words:
        if len(line1) + len(word) < 30:
            line1 += " " + word
        elif len(line2) + len(word) < 30:
            line2 += " " + word
    return [line1.strip(), line2.strip()]


def create_rgb_neon_circle(image: Image.Image, center: tuple, radius: int, border_width: int, steps: int = 30) -> Image.Image:
    # Draw a neon circular border effect on the image
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


def crop_center_circle(img: Image.Image, output_size: int, border: int, crop_scale: float = 1.5) -> Image.Image:
    # Crop image from center to create a circular thumbnail
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
    return result


async def get_thumb(videoid: str) -> str:
    # Generate a thumbnail for the YouTube video corresponding to the given video ID
    cache_path = f"cache/{videoid}_v4.png"
    if os.path.isfile(cache_path):
        return cache_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = await VideosSearch(url, limit=1).next()
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
        try:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    temp_path = f"cache/thumb{videoid}.png"
                    async with aiofiles.open(temp_path, mode="wb") as f:
                        await f.write(await resp.read())
                else:
                    return YOUTUBE_IMG_URL
        except Exception as e:
            print(f"Error downloading thumbnail: {e}")
            return YOUTUBE_IMG_URL

    try:
        youtube_img = Image.open(temp_path)
        image1 = change_image_size(1280, 720, youtube_img)
        image2 = image1.convert("RGBA")
        background = image2.filter(ImageFilter.BoxBlur(20))
        background = ImageEnhance.Brightness(background).enhance(0.6)
        draw = ImageDraw.Draw(background)

        # Create circular thumbnail with neon effect
        circle_thumbnail = crop_center_circle(youtube_img, 400, 20)
        circle_thumbnail = circle_thumbnail.resize((400, 400))
        circle_pos = (120, 160)
        background.paste(circle_thumbnail, circle_pos, circle_thumbnail)
        center = (circle_pos[0] + 200, circle_pos[1] + 200)
        create_rgb_neon_circle(background, center, 200, 10)

        # Overlay text information
        text_x = 565
        title_lines = truncate(title)
        draw.text((text_x, 180), title_lines[0], fill=(255, 255, 255), font=TITLE_FONT)
        draw.text((text_x, 230), title_lines[1], fill=(255, 255, 255), font=TITLE_FONT)
        draw.text((text_x, 320), f"{channel} | {views[:23]}", fill=(255, 255, 255), font=ARIAL_FONT)

        # Draw progress bar
        line_length = 580
        red_length = int(line_length * 0.6)
        draw.line([(text_x, 380), (text_x + red_length, 380)], fill="red", width=9)
        draw.line([(text_x + red_length, 380), (text_x + line_length, 380)], fill="white", width=8)
        circle_radius = 10
        draw.ellipse([text_x + red_length - circle_radius, 380 - circle_radius,
                      text_x + red_length + circle_radius, 380 + circle_radius], fill="red")
        draw.text((text_x, 400), "00:00", fill=(255, 255, 255), font=ARIAL_FONT)
        draw.text((1080, 400), duration, fill=(255, 255, 255), font=ARIAL_FONT)

        # Overlay play icons
        play_icons = Image.open("ERAVIBES/assets/play_icons.png").resize((580, 62))
        background.paste(play_icons, (text_x, 450), play_icons)

        background.save(cache_path)
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"Error removing temp file: {e}")

        return cache_path

    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        return YOUTUBE_IMG_URL
