import os
import sys
import asyncio
import threading
import time
import traceback
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 🎯 Telegram API Credentials
API_ID = 32815595
API_HASH = "4f8710ec9e88946139ac688af9eb1f5b"

# 🎯 Environment Variables Check
SESSION_STRING = os.getenv("SESSION_STRING", "").strip().strip('"').strip("'")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# 👑 Authorized Owners & Usernames
OWNERS = [8064395854, 8871786114]
AUTHORIZED_USERNAMES = ["Alexbro117"]
ALLOWED_PHONES = ["8116670825", "+918116670825"]

print("==================================================")
print("🔍 STARTING DIAGNOSTIC CHECKS...")
if not SESSION_STRING:
    print("❌ CRITICAL ERROR: 'SESSION_STRING' environment variable is MISSING or EMPTY!")
else:
    print(f"✅ SESSION_STRING detected (Length: {len(SESSION_STRING)})")

if not GEMINI_API_KEY:
    print("⚠️ WARNING: 'GEMINI_API_KEY' is missing! AI replies will not work.")
else:
    print("✅ GEMINI_API_KEY detected.")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"❌ GEMINI CONFIG ERROR: {e}")
print("==================================================")

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
    return "M1-!-Kriti Bot Server Status: ACTIVE & RUNNING!"

@app.route("/status")
def status():
    return {
        "status": "online",
        "session_present": bool(SESSION_STRING),
        "gemini_present": bool(GEMINI_API_KEY)
    }

# 🤖 2. Heartbeat Logger Task
async def heartbeat_task():
    while True:
        print("💓 [HEARTBEAT] Bot thread is alive and listening for Telegram events...")
        await asyncio.sleep(60)

# 🤖 3. Telegram Bot Main Loop
async def run_bot():
    print(">>> [BOT THREAD] Starting Telegram Client Initialization... <<<")
    
    if not SESSION_STRING:
        print("❌ [BOT THREAD ERROR] Cannot start Telegram Client because SESSION_STRING is missing.")
        return

    try:
        session = StringSession(SESSION_STRING)
        client = TelegramClient(session, API_ID, API_HASH)
    except Exception as e:
        print(f"❌ [SESSION ERROR] Failed to parse StringSession: {e}")
        print(traceback.format_exc())
        return

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
        try:
            if not event.is_private:
                return

            me = await client.get_me()
            if event.sender_id == me.id or event.raw_text.startswith("."):
                return

            if not await is_authorized_sender(event):
                print(f"📩 Ignored message from unauthorized sender ID: {event.sender_id}")
                return

            user_text = event.raw_text.strip()
            if not user_text:
                return

            print(f"📩 New message received from {event.sender_id}: {user_text}")

            if not GEMINI_API_KEY:
                await event.reply("Arey suno na jaan, GEMINI_API_KEY set kar do pehle! ❤️")
                return

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=kriti_wife_instruction,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            response = await asyncio.to_thread(model.generate_content, user_text)
            if response and response.text:
                await event.reply(response.text)
                print(f"📤 Reply sent: {response.text}")
            else:
                print("⚠️ Gemini response was empty or blocked by safety filters.")

        except Exception as e:
            print(f"❌ ERROR inside NewMessage handler: {e}")
            print(traceback.format_exc())

    try:
        print("🔄 Connecting to Telegram Servers...")
        await client.start()
        me = await client.get_me()
        print("==================================================")
        print(f"🎉 SUCCESS! Connected as Telegram User: {me.first_name} (@{me.username}) [ID: {me.id}]")
        print("==================================================")
        
        # Start Heartbeat Logger
        asyncio.create_task(heartbeat_task())
        
        # Keep client running indefinitely
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ TELEGRAM CONNECTION / AUTH ERROR: {e}")
        print("💡 POSSIBLE REASONS:")
        print(" 1. Your SESSION_STRING is invalid or has expired.")
        print(" 2. Telegram API ID or API HASH is incorrect.")
        print(" 3. Your IP or Telegram Account is temporarily blocked/restricted.")
        print(traceback.format_exc())

def start_bot_thread():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bot())
    except Exception as e:
        print(f"❌ CRITICAL THREAD ERROR: {e}")
        print(traceback.format_exc())

# Start Telegram Bot in background thread when script runs
bot_thread = threading.Thread(target=start_bot_thread, daemon=True)
bot_thread.start()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

if __name__ == "__main__":
    run_flask()
    
