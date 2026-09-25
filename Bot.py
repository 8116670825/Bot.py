import os
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from google import genai

# 🎯 Telegram Credentials
API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")
SESSION_STRING = os.getenv("SESSION_STRING", "").strip().replace('"', '').replace("'", "")

# 👑 Owner IDs
HUSBAND_OWNER_IDS = [8064395854, 8871786114]

# 🌐 Flask Web Server (Render ke liye)
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti AI Server Active!"

def start_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# 🤖 Telegram Client Setup
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def kriti_reply(event):
    try:
        if not event.is_private:
            return

        me = await client.get_me()
        if event.sender_id == me.id or event.sender_id not in HUSBAND_OWNER_IDS:
            return

        user_text = event.raw_text.strip()
        if not user_text:
            return

        api_key = os.getenv("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")
        if not api_key:
            return

        reply_text = ""
        async with client.action(event.chat_id, 'typing'):
            try:
                # सही और लेटेस्ट google-genai क्लाइंट इनिशियलाइज़ेशन
                genai_client = genai.Client(api_key=api_key)
                
                response = await asyncio.to_thread(
                    genai_client.models.generate_content,
                    model='gemini-2.5-flash',
                    contents=user_text,
                )
                
                if response and response.text:
                    reply_text = response.text.strip()
            except Exception as e:
                print(f"⚠️ API Error: {e}")

        if reply_text:
            await event.reply(reply_text)
        else:
            await event.reply("Suno ji, abhi connect karti hoon! 🥵💋")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print(">>> Starting Telethon Client...")
    await client.start()
    print(">>> CONNECTED! <<<")
    await client.run_until_disconnected()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Main Error: {e}")
        
