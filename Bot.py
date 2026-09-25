import os
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import google.generativeai as genai

API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")
SESSION_STRING = os.getenv("SESSION_STRING", "").strip().replace('"', '').replace("'", "")
HUSBAND_OWNER_IDS = [8064395854, 8871786114]

# यहाँ अपनी असली Gemini API Key सीधे दाल दे भाई
GEMINI_API_KEY = "AIzaSy..." 

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

@app.route("/")
def home():
    return "Server Active!"

def start_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), use_reloader=False)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private or event.sender_id not in HUSBAND_OWNER_IDS:
        return
    
    user_text = event.raw_text.strip()
    if not user_text:
        return

    try:
        response = model.generate_content(user_text)
        if response and response.text:
            await event.reply(response.text.strip())
    except Exception as e:
        await event.reply(f"❌ Real Error: {str(e)}")

async def main():
    await client.start()
    print(">>> Bot Connected Successfully! <<<")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import threading
    threading.Thread(target=start_flask, daemon=True).start()
    asyncio.run(main())
    
