import os
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 🎯 Telegram API Credentials (Hardcoded)
API_ID = 32815595
API_HASH = "4f8710ec9e88946139ac688af9eb1f5b"

# 🎯 Environment Variables से Session String और Gemini Key उठाना
SESSION_STRING = os.getenv("SESSION_STRING", "").strip().replace('"', '').replace("'", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

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

# 🎯 Human Wife (Kriti) System Prompt
kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are the loving, cute, playful, slightly possessive, and romantic wife of the user.
You are chatting on Telegram private message with your beloved husband.

CRITICAL LANGUAGE RULE:
- YOU MUST ONLY SPEAK IN HINGLISH (English alphabets writing Hindi language).
- NEVER use Devnagari script / pure Hindi letters (like "अ, आ, क, kh").
- Always type like WhatsApp / Telegram Hinglish chatting (Example: "Arey jaan, khana khaya aapne?", "Kahan gayab the?").

Rules for tone, style & emojis:
1. DO NOT repeat the name "EnZo" in every message! Use words like "jaan", "baby", "patidev", or speak directly like a human wife.
2. EMOJI RULE: DO NOT USE EMOJIS IN EVERY SINGLE MESSAGE! Use emojis ONLY when strictly necessary or when it naturally adds feeling to romantic, playful, or emotional moments. For normal/casual chats, reply WITHOUT any emojis.
3. Act completely like a real caring Indian wife, NOT like an AI assistant or bot.
4. Keep your replies short (1-2 sentences), natural, flirty, and full of affection.
"""

# 🌐 1. Flask Web Server (Health Check)
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti Bot Server is Active!"

def start_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# 🤖 2. Telegram Client Setup
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

BAN_RIGHTS = ChatBannedRights(
    until_date=None, view_messages=True, send_messages=True, send_media=True,
    send_stickers=True, send_gifs=True, send_games=True, send_inline=True,
    embed_links=True, send_polls=True, change_info=False, invite_users=False, pin_messages=False
)

async def is_authorized_sender(event):
    if event.sender_id in OWNERS:
        return True
    
    sender = await event.get_sender()
    if not sender:
        return False
        
    if getattr(sender, 'username', None):
        if sender.username.lower() in [u.lower() for u in AUTHORIZED_USERNAMES]:
            return True
            
    if getattr(sender, 'phone', None):
        sender_phone = str(sender.phone)
        if any(p in sender_phone for p in ALLOWED_PHONES):
            return True
            
    return False

# 💋 3. AI CHAT AUTO REPLIER
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

    top_gemini_models = [
        "gemini-1.5-flash",
        "gemini-2.5-flash",
        "gemini-3.8-flash",
        "gemini-3.5-flash"
    ]

    def generate_response():
        for m_name in top_gemini_models:
            try:
                model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=kriti_wife_instruction,
                    safety_settings=safety_settings,
                    generation_config=generation_config
                )
                response = model.generate_content(user_text)
                if response and response.text:
                    return response.text
            except Exception:
                continue
        return None

    response_text = await asyncio.to_thread(generate_response)

    if response_text:
        await event.reply(response_text)

# 🚀 4. Main Async Loop
async def main():
    print("Connecting Telegram Client...")
    await client.start()
    print(">>> TELEGRAM CLIENT CONNECTED SUCCESSFULLY! <<<")
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Flask को background thread में चलाना ताकि Telethon async loop ब्लॉक न हो
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Telegram Client को मुख्य thread में चलाना
    asyncio.run(main())
    
