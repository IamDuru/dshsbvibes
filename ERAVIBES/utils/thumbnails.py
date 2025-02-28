import os, re, random, math, aiofiles, aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from ERAVIBES import app
from config import YOUTUBE_IMG_URL

# Directories for assets and cache
ASSETS_DIR = "ERAVIBES/assets"
CACHE_DIR = "cache"

# Pre-load fonts for better performance
ARIAL_FONT = ImageFont.truetype(os.path.join(ASSETS_DIR, "font2.ttf"), 30)
DEFAULT_FONT = ImageFont.truetype(os.path.join(ASSETS_DIR, "font.ttf"), 30)
TITLE_FONT = ImageFont.truetype(os.path.join(ASSETS_DIR, "font3.ttf"), 45)

def change_image_size(max_width, max_height, image):
    """Image ko given dimensions ke hisaab se resize karo, aspect ratio maintain karte hue."""
    width_ratio = max_width / image.width
    height_ratio = max_height / image.height
    new_width = int(image.width * width_ratio)
    new_height = int(image.height * height_ratio)
    return image.resize((new_width, new_height))

def truncate_text(text, limit=30):
    """
    Text ko do lines me split karo, taki har line me max characters limit ho.
    Return karta hai (line1, line2).
    """
    words = text.split()
    line1, line2 = "", ""
    for word in words:
        if len(line1) + len(word) < limit:
            line1 += " " + word
        elif len(line2) + len(word) < limit:
            line2 += " " + word
    return line1.strip(), line2.strip()

def generate_light_dark_color():
    """Random RGB color generate karo jisme har channel 100 se 200 ke beech ho."""
    return (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))

def create_rgb_neon_circle(image, center, radius, border_width, steps=30):
    """Neon effect ke liye image pe ek circle draw karo."""
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

def crop_center_circle(img, output_size, border, crop_scale=1.5):
    half_width, half_height = img.width / 2, img.height / 2
    larger_size = int(output_size * crop_scale)
    cropped = img.crop((
        half_width - larger_size / 2,
        half_height - larger_size / 2,
        half_width + larger_size / 2,
        half_height + larger_size / 2
    ))
    resized = cropped.resize((output_size - 2 * border, output_size - 2 * border))
    
    final_img = Image.new("RGBA", (output_size, output_size), "white")
    mask = Image.new("L", (output_size - 2 * border, output_size - 2 * border), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, output_size - 2 * border, output_size - 2 * border), fill=255)
    final_img.paste(resized, (border, border), mask)
    
    center = (output_size // 2, output_size // 2)
    radius = (output_size - 2 * border) // 2
    return create_rgb_neon_circle(final_img, center, radius, 10)

async def get_thumb(videoid):
    """
    Thumbnail generate karo using YouTube video details.
    Agar thumbnail cache me hai to use return karo, warna download, process, aur cache karo.
    """
    cache_file = os.path.join(CACHE_DIR, f"{videoid}_v4.png")
    temp_thumb = os.path.join(CACHE_DIR, f"thumb{videoid}.png")
    
    # Agar cache file exist karti hai, directly return karo
    if os.path.isfile(cache_file):
        return cache_file

    # YouTube video details fetch karo
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = await VideosSearch(url, limit=1).next()
        if not results or not results.get("result"):
            return YOUTUBE_IMG_URL
        result = results["result"][0]
    except Exception as e:
        print(f"Error fetching YouTube details: {e}")
        return YOUTUBE_IMG_URL

    # Video ke details extract karo
    title = re.sub(r"\W+", " ", result.get("title", "Unsupported Title")).title()
    duration = result.get("duration", "Unknown Mins")
    thumbnail = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0] or YOUTUBE_IMG_URL
    views = result.get("viewCount", {}).get("short", "Unknown Views")
    channel = result.get("channel", {}).get("name", "Unknown Channel")
    
    # Thumbnail image ko async download karo
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                async with aiofiles.open(temp_thumb, "wb") as f:
                    await f.write(await resp.read())
    
    try:
        youtube_img = Image.open(temp_thumb)
        image1 = change_image_size(1280, 720, youtube_img)
        background = image1.convert("RGBA").filter(ImageFilter.BoxBlur(20))
        background = ImageEnhance.Brightness(background).enhance(0.6)
        draw = ImageDraw.Draw(background)
        
        # Circular thumbnail with neon effect
        circle_thumbnail = crop_center_circle(youtube_img, 400, 20)
        circle_thumbnail = circle_thumbnail.resize((400, 400))
        background.paste(circle_thumbnail, (120, 160), circle_thumbnail)
        
        # Text overlay
        line1, line2 = truncate_text(title)
        draw.text((565, 180), line1, fill=(255, 255, 255), font=TITLE_FONT)
        draw.text((565, 230), line2, fill=(255, 255, 255), font=TITLE_FONT)
        draw.text((565, 320), f"{channel} | {views[:23]}", fill=(255, 255, 255), font=ARIAL_FONT)
        draw.text((10, 10), "APPLE MUSIC", fill="yellow", font=DEFAULT_FONT)
        
        # Progress bar draw karo
        line_length = 580
        red_length = int(line_length * 0.6)
        draw.line([(565, 380), (565 + red_length, 380)], fill="red", width=9)
        draw.line([(565 + red_length, 380), (565 + line_length, 380)], fill="white", width=8)
        draw.ellipse([565 + red_length - 10, 380 - 10, 565 + red_length + 10, 380 + 10], fill="red")
        draw.text((565, 400), "00:00", fill=(255, 255, 255), font=ARIAL_FONT)
        draw.text((1080, 400), duration, fill=(255, 255, 255), font=ARIAL_FONT)
        
        # Play icon add karo
        play_icons_path = os.path.join(ASSETS_DIR, "play_icons.png")
        play_icons = Image.open(play_icons_path).resize((580, 62))
        background.paste(play_icons, (565, 450), play_icons)
        
        # Stroke effect (border) add karo
        stroke_width = 15
        stroke_color = generate_light_dark_color()
        stroke_image = Image.new("RGBA", (1280 + 2 * stroke_width, 720 + 2 * stroke_width), stroke_color)
        stroke_image.paste(background, (stroke_width, stroke_width))
        
        os.remove(temp_thumb)  # Temporary file delete karo
        stroke_image.save(cache_file)
        return cache_file
    except Exception as e:
        print(f"Error processing thumbnail: {e}")
        return YOUTUBE_IMG_URL
