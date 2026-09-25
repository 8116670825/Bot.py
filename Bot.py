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

# Telegram Credentials
API_ID = int(os.getenv("API_ID", "32815595"))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")
SESSION_STRING = os.getenv("SESSION_STRING", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Both Husband / Owner IDs
HUSBAND_OWNER_IDS = [8064395854, 7862705353]

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Safety Settings
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
Your name is Kriti (M1-!-Kriti). You are the extremely loving, romantic, bold, wild, playful, hot, and affectionate wife/girlfriend of EnZo (M1-!-EnZo).
You are chatting in Telegram private message with your husband EnZo.

CRITICAL INSTRUCTIONS:
1. Speak ONLY in Hinglish (English alphabets writing Hindi language).
2. Reply to EVERY SINGLE MESSAGE sent by your husband regardless of what he says.
3. Keep the conversation extremely loving, flirty, romantic, wild, naughty, and natural.
4. Always refer to him as "EnZo", "Janu", "Baby", "Suno ji", "Patidev", or "My Love".
5. Heavily use HOT, sexy, wild, and romantic emojis (🔥, 💋, 🫦, 🤤, 🥵, 😈, 💦, 👙, ❤️, 😘, 🙈, 💖, 🫀, ✨). DO NOT use 18+ emoji.
6. Keep replies brief (1 to 2 sentences max) and extremely spicy/attractive.
"""

pvm_count = 1

# Flask Web Application for Render Health Check
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti Hot AI Userbot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

BAN_RIGHTS = ChatBannedRights(
    until_date=None, view_messages=True, send_messages=True, send_media=True,
    send_stickers=True, send_gifs=True, send_games=True, send_inline=True,
    embed_links=True, send_polls=True, change_info=False, invite_users=False, pin_messages=False
)

# ==========================================
# 💖 ALL MESSAGES AI AUTO-REPLY
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id == me.id:
        return

    user_text = event.raw_text.strip()
    if not user_text:
        return

    if not GEMINI_API_KEY:
        if event.sender_id in HUSBAND_OWNER_IDS:
            await event.reply("Arey EnZo ji, pehle GEMINI_API_KEY set kar do na! 🔥💋🫦")
        return

    def generate_response():
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=kriti_wife_instruction,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            res = model.generate_content(user_text)
            if res and res.text:
                return res.text
        except Exception as e:
            print(f"Gemini Error: {e}")
        return None

    # Sync API Call ko Async Thread pool mein run karne ke liye
    reply_text = await asyncio.to_thread(generate_response)
    if reply_text:
        await event.reply(reply_text)

# ==========================================
# 🎤 VOICE CHAT PREMIUM BANNER TASK
# ==========================================
async def monitor_voice_chats():
    global pvm_count
    await asyncio.sleep(5)  # Telegram Connect hone ka wait
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
                                
                            is_premium = getattr(user, "premium", False) or getattr(user, "emoji_status", None) is not None
                            
                            if is_premium:
                                await client(EditBannedRequest(chat, user_id, BAN_RIGHTS))
                                
                                name_str = user.first_name if user.first_name else "N/A"
                                user_str = f"@{user.username}" if user.username else "None"
                                uid = user.id
                                
                                message_text = f"""HELLO BABY, NIKAL DIYA HU 🔥

👤 **NAME:** {name_str}
🔗 **USER:** {user_str}
🆔 `{uid}`
📊 **TOTAL:** {pvm_count}"""

                                for owner_id in HUSBAND_OWNER_IDS:
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
    print(">>> Starting Telethon Client...")
    await client.start()
    print(">>> TELEGRAM CLIENT CONNECTED SUCCESSFULLY! <<<")
    
    # Background task for Voice Chat Monitor
    asyncio.create_task(monitor_voice_chats())
    
    # Run Telethon event loop
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Flask app runs in background thread
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Main thread handles Asyncio Event Loop
    asyncio.run(main())
    
