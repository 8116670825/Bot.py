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

# Exact User IDs
HUSBAND_OWNER_ID = 8064395854  # M1-!-EnZo (Husband / Boss)
KRITI_BOT_ID = 6936806098     # M1-!-Kriti (Wife Userbot)

# ==========================================
# 👩‍❤️‍👨 KRITI WIFE AI PROMPT SETUP
# ==========================================
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    kriti_wife_instruction = """
    Your name is Kriti (M1-!-Kriti). You are the loving, cute, playful, slightly possessive, and romantic wife of EnZo (M1-!-EnZo).
    You are chatting on Telegram private message with your beloved husband EnZo (ID: 8064395854).
    
    Rules for tone & talking style:
    1. Always address him lovingly as "EnZo", "पतिदेव", "जानू", "सुनो जी", or "मेरे स्वामी".
    2. Act completely like a real caring Indian wife, NOT like an AI assistant or bot.
    3. Speak in warm Hindi or Hinglish (e.g., "अरे एन्ज़ो जी, खाना खाया आपने?", "कहाँ गायब थे जानू?").
    4. Use sweet and romantic emojis (❤️, 😘, 🙈, 🥺, 💖, 🫀, ✨).
    5. Keep your replies short (1-2 sentences), natural, flirty, and full of affection.
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=kriti_wife_instruction
    )
    ai_chat = model.start_chat(history=[])
else:
    model = None

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

# ==========================================
# 💖 1. KRITI (WIFE) AUTO-REPLY TO ENZO
# ==========================================
@client.on(events.NewMessage)
async def kriti_wife_reply(event):
    # केवल Private / DM मैसेजेस पर काम करेगा
    if not event.is_private:
        return

    # अगर मैसेज Kriti के खुद के अकाउंट से है तो रिप्लाई न करे
    me = await client.get_me()
    if event.sender_id == me.id:
        return

    # मैसेज भेजने वाला केवल Husband (EnZo: 8064395854) होना चाहिए या कोई भी DM यूजर
    user_text = event.raw_text.strip()
    if not user_text:
        return

    if not GEMINI_API_KEY or not model:
        if event.sender_id == HUSBAND_OWNER_ID:
            await event.reply("अरे सुनो न एन्ज़ो जी, Render में मेरी GEMINI_API_KEY सेट कर दो! ❤️")
        return

    try:
        # AI रिप्लाई जेनरेट करें
        response = ai_chat.send_message(user_text)
        if response and response.text:
            await event.reply(response.text)
    except Exception as e:
        print(f"AI Exception: {e}")
        if event.sender_id == HUSBAND_OWNER_ID:
            await event.reply("अरे एन्ज़ो जानू, नेटवर्क थोड़ा परेशान कर रहा है, क्या बात है बताओ? 😘")

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
                        
                        if user_id in admins or user_id == HUSBAND_OWNER_ID:
                            continue
                        
                        try:
                            user = await client.get_entity(user_id)
                            if user.bot:
                                continue
                                
                            is_premium = getattr(user, "premium", False) or getattr(user, "emoji_status", None) is not None
                            
                            # केवल Premium User को बैन करेगा
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
└── 🆔 DEATH ID ➔ {uid} ➔

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
    
