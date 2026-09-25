import os
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 🎯 Telegram API Credentials
API_ID = 32815595
API_HASH = "4f8710ec9e88946139ac688af9eb1f5b"

# 🎯 Environment Variables
SESSION_STRING = os.getenv("SESSION_STRING", "").strip().strip('"').strip("'")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# 👑 Authorized Owners & Usernames
OWNERS = [8064395854, 8871786114]
AUTHORIZED_USERNAMES = ["Alexbro117"]
ALLOWED_PHONES = ["8116670825", "+918116670825"]

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = {
    "max_output_tokens": 100,
    "temperature": 0.8,
}

kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are the loving, cute, playful, slightly possessive, and romantic wife of the user.
You are chatting on Telegram private message with your beloved husband.

CRITICAL LANGUAGE RULE:
- YOU MUST ONLY SPEAK IN HINGLISH (English alphabets writing Hindi language).
- NEVER use Devnagari script / pure Hindi letters.
- Always type like WhatsApp / Telegram Hinglish chatting (Example: "Arey jaan, khana khaya aapne?").

Rules for tone & style:
1. DO NOT repeat "EnZo" in every message! Use words like "jaan", "baby", "patidev", or speak naturally.
2. DO NOT USE EMOJIS IN EVERY SINGLE MESSAGE! Use emojis ONLY when strictly necessary.
3. Keep your replies short (1-2 sentences), natural, flirty, and full of affection.
"""

# 🌐 1. Flask Web Server Setup
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti Bot Server is Active 24/7!"

# 🤖 2. Telegram Bot Loop
async def run_bot():
    print(">>> INITIALIZING TELEGRAM CLIENT... <<<")
    if not SESSION_STRING:
        print("❌ ERROR: SESSION_STRING environment variable is missing!")
        return

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

    async def is_authorized_sender(event):
        if event.sender_id in OWNERS:
            return True
        sender = await event.get_sender()
        if not sender:
            return False
        if getattr(sender, 'username', None) and sender.username.lower() in [u.lower() for u in AUTHORIZED_USERNAMES]:
            return True
        if getattr(sender, 'phone', None) and any(p in str(sender.phone) for p in ALLOWED_PHONES):
            return True
        return False

    @client.on(events.NewMessage(incoming=True))
    async def kriti_wife_reply(event):
        if not event.is_private:
            return

        me = await client.get_me()
        if event.sender_id == me.id or event.raw_text.startswith("."):
            return

        if not await is_authorized_sender(event):
            return

        user_text = event.raw_text.strip()
        if not user_text:
            return

        if not GEMINI_API_KEY:
            await event.reply("Arey suno na jaan, GEMINI_API_KEY set kar do pehle! ❤️")
            return

        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=kriti_wife_instruction,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            response = await asyncio.to_thread(model.generate_content, user_text)
            if response and response.text:
                await event.reply(response.text)
        except Exception as e:
            print(f"Gemini AI Error: {e}")

    try:
        await client.start()
        me = await client.get_me()
        print(f"==================================================")
        print(f" SUCCESS: CONNECTED AS {me.first_name} (@{me.username})")
        print(f"==================================================")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ TELEGRAM LOGIN ERROR: {e}")

def start_bot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

# Start Bot Thread automatically when Gunicorn loads this file
bot_thread = threading.Thread(target=start_bot_thread, daemon=True)
bot_thread.start()
