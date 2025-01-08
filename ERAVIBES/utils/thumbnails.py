import os, re, random, aiofiles, aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from ERAVIBES import app
from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1, text2]

def generate_random_color():
    r = random.randint(0, 255)  # Random red value
    g = random.randint(0, 255)  # Random green value
    b = random.randint(0, 255)  # Random blue value
    return (r, g, b)

def crop_center_circle(img, output_size, border, crop_scale=1.5):
    half_the_width = img.size[0] / 2
    half_the_height = img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop(
        (
            half_the_width - larger_size/2,
            half_the_height - larger_size/2,
            half_the_width + larger_size/2,
            half_the_height + larger_size/2
        )
    )

    img = img.resize((output_size - 2*border, output_size - 2*border))

    # Generate a new random color for the background each time
    random_color = generate_random_color()

    # Create final_img with the random background color
    final_img = Image.new("RGBA", (output_size, output_size), random_color)

    # Create a mask for the main image
    mask_main = Image.new("L", (output_size - 2*border, output_size - 2*border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2*border, output_size - 2*border), fill=255)

    # Paste the cropped image onto the final_img using the mask
    final_img.paste(img, (border, border), mask_main)

    # Create a mask for the border
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)

    # Apply the border mask to the final image
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)

    # Return the result along with the random color
    return result, random_color
    
async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}_v4.png"):
        return f"cache/{videoid}_v4.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(url, limit=1)
    for result in (await results.next())["result"]:
        try:
            title = result["title"]
            title = re.sub("\W+", " ", title)
            title = title.title()
        except:
            title = "Unsupported Title"
        try:
            duration = result["duration"]
        except:
            duration = "Unknown Mins"
        try:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        except:
            # Agar thumbnail nahi mila, toh YOUTUBE_IMG_URL ka use karo
            return YOUTUBE_IMG_URL
        try:
            views = result["viewCount"]["short"]
        except:
            views = "Unknown Views"
        try:
            channel = result["channel"]["name"]
        except:
            channel = "Unknown Channel"

    # Agar thumbnail nahi mila, toh YOUTUBE_IMG_URL return karo
    if not thumbnail:
        return YOUTUBE_IMG_URL

    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                await f.write(await resp.read())
                await f.close()
            else:
                # Agar thumbnail download nahi hua, toh YOUTUBE_IMG_URL ka use karo
                return YOUTUBE_IMG_URL

    try:
        youtube = Image.open(f"cache/thumb{videoid}.png")
    except Exception as e:
        print(f"Error opening thumbnail image: {e}")
        return YOUTUBE_IMG_URL

    image1 = changeImageSize(1280, 720, youtube)
    image2 = image1.convert("RGBA")
    background = image2.filter(filter=ImageFilter.BoxBlur(20))
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.6)
    draw = ImageDraw.Draw(background)
    arial = ImageFont.truetype("ERAVIBES/assets/font2.ttf", 30)
    font = ImageFont.truetype("ERAVIBES/assets/font.ttf", 30)
    title_font = ImageFont.truetype("ERAVIBES/assets/font3.ttf", 45)

    # Get the circular thumbnail and the random color
    circle_thumbnail, random_color = crop_center_circle(youtube, 400, 20)
    circle_thumbnail = circle_thumbnail.resize((400, 400))
    circle_position = (120, 160)
    background.paste(circle_thumbnail, circle_position, circle_thumbnail)

    text_x_position = 565

    title1 = truncate(title)
    draw.text((text_x_position, 180), title1[0], fill=(255, 255, 255), font=title_font)
    draw.text((text_x_position, 230), title1[1], fill=(255, 255, 255), font=title_font)
    draw.text((text_x_position, 320), f"{channel}  |  {views[:23]}", (255, 255, 255), font=arial)
    draw.text((10, 10), f"ERA VIBES", fill="yellow", font=font)

    line_length = 580  

    red_length = int(line_length * 0.6)
    white_length = line_length - red_length

    start_point_red = (text_x_position, 380)
    end_point_red = (text_x_position + red_length, 380)
    draw.line([start_point_red, end_point_red], fill="red", width=9)

    start_point_white = (text_x_position + red_length, 380)
    end_point_white = (text_x_position + line_length, 380)
    draw.line([start_point_white, end_point_white], fill="white", width=8)

    circle_radius = 10 
    circle_position = (end_point_red[0], end_point_red[1])
    draw.ellipse([circle_position[0] - circle_radius, circle_position[1] - circle_radius,
                  circle_position[0] + circle_radius, circle_position[1] + circle_radius], fill="red")
    draw.text((text_x_position, 400), "00:00", (255, 255, 255), font=arial)
    draw.text((1080, 400), duration, (255, 255, 255), font=arial)

    play_icons = Image.open("ERAVIBES/assets/play_icons.png")
    play_icons = play_icons.resize((580, 62))
    background.paste(play_icons, (text_x_position, 450), play_icons)

    # Add a stroke to the entire image using the same random color
    stroke_width = 10
    stroke_image = Image.new("RGBA", (1280 + 2*stroke_width, 720 + 2*stroke_width), random_color)
    stroke_image.paste(background, (stroke_width, stroke_width))

    try:
        os.remove(f"cache/thumb{videoid}.png")
    except:
        pass
    stroke_image.save(f"cache/{videoid}_v4.png")
    return f"cache/{videoid}_v4.png"
