from ERAVIBES import app  # ERAVIBES module se app object import karen
from pyrogram import filters
import requests

# Sugoi API endpoint
SUGOI_API_URL = "https://sugoi-api.vercel.app/chat"

# System prompt (Cute and kind girl ke tone mein)
SYSTEM_PROMPT = (
    "You are a cute, kind, and sweet Indian girl who talks in a friendly and loving tone. "
    "You always respond with warmth and care, using a mix of Hindi and English (Hinglish). "
    "You love making people happy and always try to cheer them up with your words. "
    "You use emojis like 😊, 🥰, 💖, 🌸 to express your emotions. "
    "You are always positive, avoid negative or rude responses, and make the conversation engaging. "
    "Your goal is to make the user feel special and keep them talking to you."
)

# Message handler (sirf private messages ke liye)
@app.on_message(filters.private & filters.text)
def handle_message(client, message):
    user_message = message.text

    # API request data
    data = {
        "msg": user_message,
        "system": SYSTEM_PROMPT  # System prompt add kiya gaya hai
    }

    try:
        # Sugoi API ko call karein
        response = requests.post(SUGOI_API_URL, json=data, timeout=10)  # 10 seconds timeout
        
        # Check karein ki response sahi hai ya nahi
        if response.status_code == 200:
            json_response = response.json()
            
            # "response" field ko extract karein
            if "response" in json_response:
                ai_response = json_response["response"]
                message.reply_text(ai_response)
            else:
                # Agar "response" field nahin hai
                message.reply_text("Mujhe lagta hai API ne sahi response nahin diya. Kya aap dobara try kar sakte hain? 😊")
        else:
            # Agar API se error aa raha hai
            message.reply_text(f"API se error aa raha hai. Status code: {response.status_code}. Kya aap dobara try kar sakte hain? 😊")
    
    except requests.exceptions.RequestException as e:
        # Agar API call mein koi exception aata hai
        message.reply_text(f"API se connect nahin ho pa raha hai. Error: {str(e)}. Kya aap dobara try kar sakte hain? 😊")
