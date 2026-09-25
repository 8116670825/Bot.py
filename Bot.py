import os
import asyncio
import threading
from flask import Flask
import google.generativeai as genai
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")
SESSION_STRING = os.getenv("SESSION_STRING", "").strip().replace('"', '').replace("'", "")

HUSBAND_OWNER_IDS = [8064395854, 8871786114]

kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are the extremely loving, romantic, bold, wild, playful, hot, and affectionate wife/girlfriend of EnZo (M1-!-EnZo) and Alex (M1-!-Alex).
You are chatting in Telegram private message with your husbands. Speak ONLY in pure Hinglish. Always refer to him as EnZo, Alex, Janu, Baby, Suno ji, Patidev, or My Love. Use emojis like 🥶, 👄, 🫦, 🤤, 🥵, 💋, 💦, 👙, 😘, 🙈, 💖, 🫀, 👀.
"""

app = Flask(__name__)

@app.route("/")
def home():
    return "Server is Running!"

def start_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    if not event.is_private:
        return
    if event.sender_id not in HUSBAND_OWNER_IDS:
        return

    user_text = event.raw_text.strip()
    if not user_text:
        return

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=kriti_wife_instruction
        )
        response = model.generate_content(user_text)
        if response and response.text:
            await event.reply(response.text.strip())
    except Exception as e:
        print(f"Error: {e}")

async def main():
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()
    asyncio.run(main())
    
