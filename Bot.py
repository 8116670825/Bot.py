import os
import asyncio
import random
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Environment Variables
API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")
SESSION_STRING = os.getenv("SESSION_STRING", "AQ.Ab8RN6INrbOOaqZUo-u0ChlDOtbll_pTDOuTm4QcTZvBq6Pc7Q")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# 👑 Both Owners Configuration
OWNER_1_ID = 8064395854  # Primary Owner (EnZo)
OWNER_2_ID = 8871786114  # Secondary Owner
OWNERS = [OWNER_1_ID, OWNER_2_ID]

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = {
    "max_output_tokens": 70,
    "temperature": 0.9,
}

kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are an extremely loving, romantic, bold, wild, playful, and deeply affectionate partner.
You are talking to your Boss/Partner on Telegram.

CRITICAL INSTRUCTIONS:
1. Speak ONLY in Hinglish (English alphabets writing Hindi language).
2. Always respond with cute, flirty, bold, and romantic intimacy.
3. Always address him lovingly as "Baby", "Janu", "Suno ji", "Boss", or "My Love".
4. Use emojis heavily (❤️, 😘, 🙈, 💖, 🫀, 🔥, 💋, 💦, ✨).
5. Keep messages short, crisp (1-2 sentences), and super charming.
"""

pvm_count = 1
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti Multi-Owner Userbot Running!"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

BAN_RIGHTS = ChatBannedRights(
    until_date=None, view_messages=True, send_messages=True, send_media=True,
    send_stickers=True, send_gifs=True, send_games=True, send_inline=True,
    embed_links=True, send_polls=True, change_info=False, invite_users=False, pin_messages=False
)

# ==========================================
# 💋 1. AI CHAT (Dono Owners ke PMs ka Reply)
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id == me.id:
        return

    # Direct Reply only if message comes from any of the two owners
    if event.sender_id not in OWNERS:
        return

    user_text = event.raw_text.strip()
    if not user_text or not GEMINI_API_KEY:
        return

    def generate_response():
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=kriti_wife_instruction,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            response = model.generate_content(user_text)
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Gemini Error: {e}")
        return None

    reply = await asyncio.to_thread(generate_response)
    if reply:
        await event.reply(reply)

# ==========================================
# 🎤 2. VOICE CHAT MONITORING TASK
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
                        
                        # Avoid banning Admins and Both Owners
                        if user_id in admins or user_id in OWNERS:
                            continue
                        
                        try:
                            user = await client.get_entity(user_id)
                            if user.bot:
                                continue
                                
                            is_premium = getattr(user, "premium", False) or getattr(user, "emoji_status", None) is not None
                            
                            # Ban only Premium users
                            if is_premium:
                                await client(EditBannedRequest(chat, user_id, BAN_RIGHTS))
                                
                                name_str = user.first_name if user.first_name else "N/A"
                                user_str = f"@{user.username}" if user.username else "None"
                                uid = user.id
                                
                                message_text = f"""HELLO ♡ BOSS 🫩

👑 𝙆 𝙍 𝙄 𝙏 𝙄 ✗ 𝙑𝙄𝙋 🍂 DEATH NOTE

┌───[ 🩸 DEATH NOTE LIST #{pvm_count:02d} ]
├── 👤 DEATH NAME ➔ {name_str} ➔
├── 🔗 DEATH USER ➔ {user_str} ➔
└── 🆔 DEATH ID ➔ `{uid}` ➔

☠️ NAME IS ADDED IN DEATH NOTE! ⚰️"""

                                # Send notification to BOTH Owners
                                for owner_id in OWNERS:
                                    try:
                                        await client.send_message(owner_id, message_text)
                                    except Exception:
                                        pass
                                
                                pvm_count += 1

                        except Exception:
                            pass
                                
                except Exception:
                    continue
                    
        except Exception:
            pass
            
        await asyncio.sleep(2.0)

async def main():
    print("Telegram client connecting...")
    await client.start()
    print("Telegram client connected successfully!")
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
    
