import os
import asyncio
import google.generativeai as genai
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

# Telegram Credentials
API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")

SESSION_STRING = os.getenv("SESSION_STRING", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# 🎯 Authorized IDs (First ID)
HUSBAND_OWNER_IDS = [8064395854]

# 🎯 Authorized Usernames (Second ID Username)
AUTHORIZED_USERNAMES = ["Alexbro117"]

# 🎯 Authorized Phone Numbers
ALLOWED_PHONES = ["8116670825", "+918116670825"]

# 🔔 डिफ़ॉल्ट बैन मैसेज
DYNAMIC_BAN_MESSAGE = """HELLO ♡ M1-!-EnZo BOSS,

👑 𝙆 𝙍 𝙄 𝙏 𝙄 ✗ 𝙑𝙄𝙋 🍂 DEATH NOTE

┌───[ 🩸 DEATH NOTE LIST #{count:02d} ]
├── 👤 DEATH NAME ➔ {name} ➔
├── 🔗 DEATH USER ➔ {username} ➔
└── 🆔 DEATH ID ➔ `{id}` ➔

☠️ NEW FLAG / PREMIUM USER BANNED FROM {title}! ⚰️"""

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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

pvm_count = 1
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti Wife AI Userbot is Running!"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

BAN_RIGHTS = ChatBannedRights(
    until_date=None, view_messages=True, send_messages=True, send_media=True,
    send_stickers=True, send_gifs=True, send_games=True, send_inline=True,
    embed_links=True, send_polls=True, change_info=False, invite_users=False, pin_messages=False
)

async def is_authorized_sender(event):
    """Checks if sender matches First ID, Second Username, or Phone Number"""
    if event.sender_id in HUSBAND_OWNER_IDS:
        return True
    
    sender = await event.get_sender()
    if not sender:
        return False
        
    # Check Username
    if getattr(sender, 'username', None):
        if sender.username.lower() in [u.lower() for u in AUTHORIZED_USERNAMES]:
            return True
            
    # Check Phone Number
    if getattr(sender, 'phone', None):
        sender_phone = str(sender.phone)
        if any(p in sender_phone for p in ALLOWED_PHONES):
            return True
            
    return False

# ==========================================
# ⚙️ 1. DYNAMIC MESSAGE SETTER COMMANDS (.setmsg & .getmsg)
# ==========================================
@client.on(events.NewMessage)
async def manage_ban_message(event):
    if not await is_authorized_sender(event):
        return

    global DYNAMIC_BAN_MESSAGE
    text = event.raw_text

    if text.startswith(".setmsg"):
        new_msg = text.replace(".setmsg", "").strip()
        if new_msg:
            DYNAMIC_BAN_MESSAGE = new_msg
            await event.reply("✅ **Ban Message Successfully Updated!**")
        else:
            await event.reply("❌ **Error:** मैसेज खाली नहीं हो सकता।")

    elif text.strip() == ".getmsg":
        await event.reply(f"📌 **Current Ban Message Template:**\n\n```\n{DYNAMIC_BAN_MESSAGE}\n```")

# ==========================================
# 💖 2. KRITI (HUMAN WIFE) AUTO-REPLY FOR PRIVATE CHATS
# ==========================================
@client.on(events.NewMessage)
async def kriti_wife_reply(event):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id == me.id or event.raw_text.startswith("."):
        return

    # Check if message is from Boss (First ID or Second Username @Alexbro117)
    if not await is_authorized_sender(event):
        return

    user_text = event.raw_text.strip()
    if not user_text:
        return

    if not GEMINI_API_KEY:
        await event.reply("Arey suno na jaan, GEMINI_API_KEY set kar do pehle!")
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
                    system_instruction=kriti_wife_instruction
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

# ==========================================
# 🎤 3. VOICE CHAT MONITORING TASK
# ==========================================
async def monitor_voice_chats():
    global pvm_count, DYNAMIC_BAN_MESSAGE
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
                        
                        if user_id in admins or user_id in HUSBAND_OWNER_IDS:
                            continue
                        
                        try:
                            user = await client.get_entity(user_id)
                            if user.bot:
                                continue
                                
                            has_flag_emoji = getattr(user, "emoji_status", None) is not None
                            is_premium = getattr(user, "premium", False)
                            
                            if is_premium or has_flag_emoji:
                                await client(EditBannedRequest(chat, user_id, BAN_RIGHTS))
                                
                                channel_title = chat.title if hasattr(chat, 'title') else "Private"
                                name_str = user.first_name if user.first_name else "N/A"
                                user_str = f"@{user.username}" if user.username else "None"
                                uid = user.id
                                
                                try:
                                    message_text = DYNAMIC_BAN_MESSAGE.format(
                                        count=pvm_count,
                                        name=name_str,
                                        username=user_str,
                                        id=uid,
                                        title=channel_title
                                    )
                                except Exception:
                                    message_text = DYNAMIC_BAN_MESSAGE

                                try:
                                    await client.send_message(HUSBAND_OWNER_IDS[0], message_text)
                                    pvm_count += 1
                                except Exception:
                                    pass

                        except Exception:
                            pass
                                
                except Exception:
                    continue
                    
        except Exception:
            pass
            
        await asyncio.sleep(1.0)

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
    
