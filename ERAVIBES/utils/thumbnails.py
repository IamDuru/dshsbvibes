import os, re, math, aiofiles, aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

ARIAL_FONT = ImageFont.truetype("ERAVIBES/assets/font2.ttf", 30)
TITLE_FONT = ImageFont.truetype("ERAVIBES/assets/font3.ttf", 45)

def change_image_size(max_width: int, max_height: int, image: Image.Image) -> Image.Image:
    width_ratio = max_width / image.size[0]
    height_ratio = max_height / image.size[1]
    new_width = int(width_ratio * image.size[0])
    new_height = int(height_ratio * image.size[1])
    return image.resize((new_width, new_height))

def truncate(text: str) -> list:
    words = text.split(" ")
    line1, line2 = "", ""
    for word in words:
        if len(line1) + len(word) < 30:
            line1 += " " + word
        elif len(line2) + len(word) < 30:
            line2 += " " + word
    return [line1.strip(), line2.strip()]

def crop_center_circle(img: Image.Image, output_size: int, border: int, crop_scale: float = 1.5) -> Image.Image:
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

def add_neon_glow(image: Image.Image, center: tuple, radius: int, glow_color: tuple = (0, 200, 255), blur_radius: int = 20) -> Image.Image:
    # Create a new layer for glow and draw a filled circle with partial transparency
    glow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.ellipse([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius], fill=glow_color + (180,))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(blur_radius))
    return Image.alpha_composite(image, glow_layer)

async def get_thumb(videoid: str) -> str:
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

        # Create background with blurred video thumbnail
        bg_img = change_image_size(1280, 720, youtube_img)
        bg_img = bg_img.convert("RGBA")
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(20))
        bg_img = ImageEnhance.Brightness(bg_img).enhance(0.6)
        draw = ImageDraw.Draw(bg_img)

        # Process circular thumbnail with a subtle drop shadow
        circle_thumbnail = crop_center_circle(youtube_img, 400, 20)
        circle_thumbnail = circle_thumbnail.resize((400, 400))
        circle_pos = (120, 160)
        shadow = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.ellipse((10, 10, 400, 400), fill=(0, 0, 0, 100))
        bg_img.paste(shadow, (circle_pos[0]+5, circle_pos[1]+5), shadow)
        bg_img.paste(circle_thumbnail, circle_pos, circle_thumbnail)

        # Add a refined neon glow around the circular image using a subtle blur
        center = (circle_pos[0] + 200, circle_pos[1] + 200)
        bg_img = add_neon_glow(bg_img, center, 210, glow_color=(0, 200, 255), blur_radius=20)

        # Overlay text details
        text_x = 565
        title_lines = truncate(title)
        draw.text((text_x, 180), title_lines[0], fill=(255, 255, 255), font=TITLE_FONT)
        draw.text((text_x, 230), title_lines[1], fill=(255, 255, 255), font=TITLE_FONT)
        draw.text((text_x, 320), f"{channel} | {views[:23]}", fill=(255, 255, 255), font=ARIAL_FONT)
        line_length = 580
        red_length = int(line_length * 0.6)
        draw.line([(text_x, 380), (text_x + red_length, 380)], fill="red", width=9)
        draw.line([(text_x + red_length, 380), (text_x + line_length, 380)], fill="white", width=8)
        circle_radius = 10
        draw.ellipse([text_x + red_length - circle_radius, 380 - circle_radius,
                      text_x + red_length + circle_radius, 380 + circle_radius], fill="red")
        draw.text((text_x, 400), "00:00", fill=(255, 255, 255), font=ARIAL_FONT)
        draw.text((1080, 400), duration, fill=(255, 255, 255), font=ARIAL_FONT)

        play_icons = Image.open("ERAVIBES/assets/play_icons.png").resize((580, 62))
        bg_img.paste(play_icons, (text_x, 450), play_icons)

        bg_img.save(cache_path)
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"Error removing temp file: {e}")
        return cache_path

    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        return YOUTUBE_IMG_URL
