from pyrogram import filters
import feedparser
from ERAVIBES import app  # Importing from ERAVIBES

# Function to fetch news based on user query
def fetch_news(query):
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"  # Corrected URL
    feed = feedparser.parse(rss_url)

    # Extract top 5 news articles
    news_list = [(entry.title, entry.link) for entry in feed.entries[:5]]

    return news_list

# /news <query> command handler
@app.on_message(filters.command("news"))
def send_news(client, message):
    # Check if query is provided
    if len(message.command) < 2:
        message.reply_text("❌ Usage: <code>/news topic</code> (e.g., <code>/news India</code>)", parse_mode="html")
        return

    query = " ".join(message.command[1:])  # Extract query from command
    news_list = fetch_news(query)

    if not news_list:
        message.reply_text(f"❌ '{query}' par koi news nahi mili.", parse_mode="html")
        return

    # HTML formatting for links
    news_text = f"📰 <b>{query.capitalize()} News:</b>\n\n"
    for i, (title, link) in enumerate(news_list, 1):
        news_text += f"🔹 {i}. <a href='{link}'>{title}</a>\n"

    message.reply_text(news_text, parse_mode="html", disable_web_page_preview=True)

print("✅ News command loaded successfully!")
