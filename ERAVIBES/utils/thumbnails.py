import os
import re
import math
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

# Global fonts – baar baar disk access na ho
ARIAL_FONT = ImageFont.truetype("ERAVIBES/assets/font2.ttf", 30)
TITLE_FONT = ImageFont.truetype("ERAVIBES/assets/font3.ttf", 45)

def change_image_size(max_width: int, max_height: int, image: Image.Image) -> Image.Image:
    # Aspect ratio maintain karte hue image resize karta hai
    width_ratio = max_width / image.size[0]
    height_ratio = max_height / image.size[1]
    new_width = int(width_ratio * image.size[0])
    new_height = int(height_ratio * image.size[1])
    return image.resize((new_width, new_height))

def truncate(text: str) -> list:
    # Text ko do lines mein split karta hai (lagbhag 30 characters per line)
    words = text.split(" ")
    line1, line2 = "", ""
    for word in words:
        if len(line1) + len(word) < 30:
            line1 += " " + word
        elif len(line2) + len(word) < 30:
            line2 += " " + word
    return [line1.strip(), line2.strip()]

def crop_center_circle(img: Image.Image, output_size: int, border: int, crop_scale: float = 1.5) -> Image.Image:
    # Image ko center se crop karke circular thumbnail banata hai
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
    mask = Image.new("L", (output_size - 2 * border, output_size - 2 * border), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, output_size - 2 * border, output_size - 2 * border), fill=255)
    final_img.paste(img, (border, border), mask)
    return final_img

async def get_thumb(videoid: str) -> str:
    # Generate professional looking thumbnail for the given YouTube video ID
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

        # Create blurred background from video thumbnail
        bg_img = change_image_size(1280, 720, youtube_img)
        bg_img = bg_img.convert("RGBA")
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(25))
        bg_img = ImageEnhance.Brightness(bg_img).enhance(0.5)

        # Add semi-transparent overlay for a professional look
        overlay = Image.new("RGBA", bg_img.size, (0, 0, 0, 120))
        background = Image.alpha_composite(bg_img, overlay)

        draw = ImageDraw.Draw(background)

        # Create circular thumbnail with a white border
        circle_img = crop_center_circle(youtube_img, 400, 20)
        circle_border = Image.new("RGBA", (400, 400), (255, 255, 255, 0))
        border_draw = ImageDraw.Draw(circle_border)
        border_draw.ellipse((0, 0, 400, 400), outline="white", width=10)
        circle_pos = (80, 160)
        background.paste(circle_img, circle_pos, circle_img)
        background.paste(circle_border, circle_pos, circle_border)

        # Draw a semi-transparent rectangle for text background on right side
        rect_x, rect_y = 500, 150
        rect_width, rect_height = 640, 400
        rect_overlay = Image.new("RGBA", (rect_width, rect_height), (0, 0, 0, 180))
        background.paste(rect_overlay, (rect_x, rect_y), rect_overlay)

        # Write video details on the rectangle with clean fonts
        title_lines = truncate(title)
        text_x, text_y = rect_x + 20, rect_y + 20
        draw.text((text_x, text_y), title_lines[0], font=TITLE_FONT, fill="white")
        draw.text((text_x, text_y + 50), title_lines[1], font=TITLE_FONT, fill="white")
        info_text = f"{channel} | {views} | {duration}"
        draw.text((text_x, text_y + 120), info_text, font=ARIAL_FONT, fill="white")

        background.save(cache_path)
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"Error removing temp file: {e}")
        return cache_path

    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        return YOUTUBE_IMG_URL
