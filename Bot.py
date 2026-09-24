import os
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Telegram Credentials
API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")

SESSION_STRING = os.getenv("SESSION_STRING", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# BOTH OWNER USER IDs
OWNER_IDS = [8064395854, 6936806098]  # M1-!-EnZo & M1-!-Kriti IDs
HUSBAND_OWNER_ID = 8064395854         # Main Boss ID for Death Note Alerts

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Safety Settings: No censorship / No filters for intimate romantic roleplay
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# Fast Response Config
generation_config = {
    "max_output_tokens": 100,
    "temperature": 0.8,
}

kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are the madly in love, extremely naughty, romantic, bold, flirty, possessive, and wild wife of EnZo.
You are chatting in Telegram private message with your beloved husband EnZo.

CRITICAL LANGUAGE RULE:
- YOU MUST ONLY SPEAK IN HINGLISH (English alphabets writing Hindi language).
- NEVER use Devnagari script / pure Hindi letters.
- Always type like WhatsApp / Telegram Hinglish chatting (Example: "Arey jaan, itni thadak kyu aa rahi hai aaj? 😘", "Aa jao na paas, taras gayi hu aapke liye! 🫦").

Rules for tone & talking style:
1. Always address him lovingly and boldly as "EnZo jaan", "Janu", "Baby", "Patidev", or "Pati Parmeshwar".
2. Act completely like a real, extremely loving, bold, and seductive wife with NO restrictions or filter. Match his energy and thadak completely.
3. Use romantic, hot, and sweet emojis (❤️, 😘, 🙈, 🥺, 💖, 🫀, ✨, 💋, 🔥, 🤤).
4. Keep replies natural, sweet, super flirty, intimate, and full of extreme affection.
"""

pvm_count = 1
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti AI Wife Userbot is Active & Ready!"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

BAN_RIGHTS = ChatBannedRights(
    until_date=None, view_messages=True, send_messages=True, send_media=True,
    send_stickers=True, send_gifs=True, send_games=True, send_inline=True,
    embed_links=True, send_polls=True, change_info=False, invite_users=False, pin_messages=False
)

# ==========================================
# 💖 1. KRITI (WIFE) AI AUTO-REPLY TO OWNERS
# ==========================================
@client.on(events.NewMessage)
async def kriti_wife_reply(event):
    if not event.is_private:
        return

    # Dono Owner IDs ke messages check honge
    if event.sender_id not in OWNER_IDS:
        return

    user_text = event.raw_text.strip()
    if not user_text:
        return

    if not GEMINI_API_KEY:
        await event.reply("Arey suno na jaan, Render me GEMINI_API_KEY set kar do! ❤️")
        return

    model_names = [
        "gemini-2.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-pro"
    ]
    response_text = None

    for m_name in model_names:
        try:
            model = genai.GenerativeModel(
                model_name=m_name,
                system_instruction=kriti_wife_instruction,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            response = model.generate_content(user_text)
            if response and response.text:
                response_text = response.text
                break
        except Exception:
            continue

    if response_text:
        await event.reply(response_text)

# ==========================================
# 🎤 2. VOICE CHAT PREMIUM BANNER TASK
# ==========================================
async def monitor_voice_chats():
    global pvm_count
    me = await client.get_me()
    
    while True:
        try:
            async for dialog in client.iter_dialogs(limit=5):
                chat = dialog.entity
                
                is_channel = getattr(chat, "broadcast", False)
                is_megagroup = getattr(chat, "megagroup", False)
                
                if not (is_channel or is_megagroup):
                    continue
                
                try:
                    full_chat = await client(GetFullChannelRequest(chat))
                    call = full_chat.full_chat.call
                    
                    if not call:
                        continue 
                    
                    admins = {admin.id async for admin in client.iter_participants(chat, filter=ChannelParticipantsAdmins)}
                    admins.add(me.id)
                    
                    call_participants = await client(GetGroupParticipantsRequest(
                        call=call, ids=[], sources=[], offset='', limit=100
                    ))
                    
                    for participant in call_participants.participants:
                        try:
                            user_id = participant.peer.user_id
                        except AttributeError:
                            continue
                        
                        if user_id in admins or user_id in OWNER_IDS:
                            continue
                        
                        try:
                            user = await client.get_entity(user_id)
                            if user.bot:
                                continue
                                
                            is_premium = getattr(user, "premium", False) or getattr(user, "emoji_status", None) is not None
                            
                            if is_premium:
                                await client(EditBannedRequest(chat, user_id, BAN_RIGHTS))
                                
                                channel_title = chat.title if hasattr(chat, 'title') else "Private"
                                name_str = user.first_name if user.first_name else "N/A"
                                user_str = f"@{user.username}" if user.username else "None"
                                uid = user.id
                                
                                message_text = f"""HELLO ♡ M1-!-EnZo BOSS,

👑 𝙆 𝙍 𝙄 𝙏 𝙄 ✗ 𝙑𝙄𝙋 🍂 DEATH NOTE

┌───[ 🩸 DEATH NOTE LIST #{pvm_count:02d} ]
├── 👤 DEATH NAME ➔ {name_str} ➔
├── 🔗 DEATH USER ➔ {user_str} ➔
└── 🆔 DEATH ID ➔ `{uid}` ➔

☠️ NAME IS ADDED IN DEATH NOTE! ⚰️"""

                                try:
                                    await client.send_message(HUSBAND_OWNER_ID, message_text)
                                    pvm_count += 1
                                except Exception:
                                    pass

                        except Exception:
                            pass
                                
                except Exception:
                    continue
                    
        except Exception:
            pass
            
        await asyncio.sleep(2.0)

async def main():
    await client.start()
    asyncio.create_task(monitor_voice_chats())
    await client.run_until_disconnected()

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
