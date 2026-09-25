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

# 🎯 Telegram Credentials
API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")
SESSION_STRING = os.getenv("SESSION_STRING", "").strip().replace('"', '').replace("'", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# 👑 आपकी दोनों असली PRIMARY OWNER IDs
OWNER_1 = 8064395854
OWNER_2 = 8871786114
PRIMARY_OWNERS = [OWNER_1, OWNER_2]

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
    "temperature": 0.8,
}

kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are the extremely loving, romantic, bold, playful, and affectionate wife of your husband (Owner).
You are chatting in Telegram private message with your husband EnZo.

CRITICAL INSTRUCTIONS:
1. Speak ONLY in Hinglish (English alphabets writing Hindi language).
2. Reply to EVERY SINGLE MESSAGE sent by your husband regardless of what he says.
3. Keep the conversation extremely loving, flirty, romantic, and natural.
4. Always refer to him as "EnZo", "Janu", "Baby", "Suno ji", "Patidev", or "Boss".
5. Use cute/romantic emojis (❤️, 😘, 🙈, 💖, 🫀, ✨, 🔥).
6. Keep replies brief (1 to 2 sentences max) and fast.
"""

MODELS_TO_TRY = [
    "gemini-2.0-flash",          
    "gemini-2.0-flash-lite",     
    "gemini-1.5-flash",          
    "gemini-1.5-flash-8b",       
    "gemini-1.5-pro",            
    "gemini-1.0-pro"             
]

pvm_count = 1
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti AI Userbot is Running!"

try:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
except Exception as err:
    print(f"CRITICAL SESSION ERROR: {err}")

BAN_RIGHTS = ChatBannedRights(
    until_date=None, view_messages=True, send_messages=True, send_media=True,
    send_stickers=True, send_gifs=True, send_games=True, send_inline=True,
    embed_links=True, send_polls=True, change_info=False, invite_users=False, pin_messages=False
)

async def generate_fast_response(prompt_text):
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
        except Exception:
            continue
    return None

# ==========================================
# 💖 AI AUTO-REPLY (केवल आपकी दोनों IDs के लिए)
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id == me.id:
        return

    # सिर्फ आपकी दोनों IDs पर ही रिप्लाई करेगा
    if event.sender_id not in PRIMARY_OWNERS:
        return

    user_text = event.raw_text.strip()
    if not user_text:
        return

    if not GEMINI_API_KEY:
        await event.reply("Arey Suno ji, pehle GEMINI_API_KEY set kar do na! ❤️")
        return

    reply_text = await generate_fast_response(user_text)

    if reply_text:
        try:
            await event.reply(reply_text)
        except Exception as e:
            print(f"Error in reply: {e}")

# ==========================================
# 🎤 VOICE CHAT MONITOR TASK
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
                        
                        # Admins और आपकी दोनों IDs पूरी तरह सुरक्षित रहेंगी
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
                                
                                message_text = f"""HELLO BABY, NIKAL DIYA HU 🔥

👤 **NAME:** {name_str}
🔗 **USER:** {user_str}
🆔 `{uid}`
📊 **TOTAL:** {pvm_count}"""

                                # दोनों Owner IDs पर मैसेज जाएगा
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
    await client.start()
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
    
