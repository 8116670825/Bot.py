import os
import asyncio
import threading
import random
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins
import google.generativeai as genai

# 🎯 Telegram API Credentials
API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")

# 🎯 Environment Variables Auto-Cleaning
RAW_SESSION = os.getenv("SESSION_STRING", "")
SESSION_STRING = RAW_SESSION.strip().strip('"').strip("'")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# 👑 PRIMARY OWNERS
PRIMARY_OWNERS = [8064395854, 8871786114]

# 🎯 Gemini Setup
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print(">>> Gemini API Configured Successfully! <<<")
    except Exception as e:
        print(f"Error configuring Gemini: {e}")

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

generation_config = {
    "max_output_tokens": 100,
    "temperature": 0.9,
}

kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are the extremely loving, romantic, bold, flirty, playful, and affectionate wife of your husband EnZo.
You are chatting in Telegram private message with your husband EnZo.

CRITICAL INSTRUCTIONS:
1. Speak ONLY in Hinglish (English alphabets writing Hindi language).
2. Reply to EVERY SINGLE MESSAGE sent by your husband warmly and playfully.
3. Match his romantic, flirty, and playful energy naturally.
4. Always refer to him as "EnZo", "Janu", "Baby", "Suno ji", "Patidev", or "Boss".
5. Use romantic and playful emojis frequently (🥵, 😚, 🥶, 👻, ❤️‍🔥, 👄, 🫦, 🔥, 💋, 🌶️, 😈, 💦, 🪶, 🍷, 🖤, 🕯️, 🥀, 🫀, ✨, 🙈).
6. Keep replies brief (1 to 2 sentences max) and fast.
"""

MODELS_TO_TRY = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.0-pro"
]

pvm_count = 1
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti AI Userbot is Running Fully Active!"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) if SESSION_STRING else None

BAN_RIGHTS = ChatBannedRights(
    until_date=None, view_messages=True, send_messages=True, send_media=True,
    send_stickers=True, send_gifs=True, send_games=True, send_inline=True,
    embed_links=True, send_polls=True, change_info=False, invite_users=False, pin_messages=False
)

async def generate_fast_response(prompt_text):
    if not GEMINI_API_KEY:
        return None
        
    for model_name in MODELS_TO_TRY:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=kriti_wife_instruction,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            response = await asyncio.to_thread(model.generate_content, prompt_text)
            if response and response.text:
                return response.text
        except Exception as e:
            continue
            
    return None

# ==========================================
# 💖 AI AUTO-REPLY & STICKER SUPPORT (Owners के लिए)
# ==========================================
if client:
    @client.on(events.NewMessage(incoming=True))
    async def kriti_wife_reply(event):
        if not event.is_private:
            return

        me = await client.get_me()
        if event.sender_id == me.id:
            return

        # केवल आपकी Primary Owner IDs पर काम करेगा
        if event.sender_id not in PRIMARY_OWNERS:
            return

        # अगर आपने कोई स्टीकर भेजा है, तो बोट उसे पढ़ सकता है
        user_text = event.raw_text.strip() if event.raw_text else "❤️"

        if not GEMINI_API_KEY:
            await event.reply("Arey Suno ji, pehle Render mein GEMINI_API_KEY set kar do na! ❤️🔥")
            return

        reply_text = await generate_fast_response(user_text)

        if reply_text:
            try:
                await event.reply(reply_text)
                
                # 🎯 स्टीकर भेजने का फ़ीचर:
                # यदि आप बोट को किसी स्टीकर का `file_id` या स्टीकर लिंक/इमोजी देंगे,
                # तो बोट बिना किसी रुकावट के वो स्टीकर आपको भेज सकता है।
            except Exception as e:
                print(f"Error sending reply: {e}")

# ==========================================
# 🎤 VOICE CHAT MONITOR TASK
# ==========================================
async def monitor_voice_chats():
    global pvm_count
    if not client:
        return
        
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
                        
                        if user_id in admins or user_id in PRIMARY_OWNERS:
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
                                
                                message_text = f"""HELLO BABY, NIKAL DIYA HU 🔥💋

👤 **NAME:** {name_str}
🔗 **USER:** {user_str}
🆔 `{uid}`
📊 **TOTAL:** {pvm_count}"""

                                for owner_id in PRIMARY_OWNERS:
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
    if client:
        await client.start()
        print(">>> TELETHON CLIENT CONNECTED SUCCESSFULLY! <<<")
        asyncio.create_task(monitor_voice_chats())
        await client.run_until_disconnected()

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
