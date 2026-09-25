import os
import asyncio
import threading
import traceback
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

# 👑 Owner IDs (Alex & EnZo)
HUSBAND_OWNER_IDS = [8064395854, 8871786114]

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = {
    "max_output_tokens": 250,
    "temperature": 0.9,
}

kriti_wife_instruction = """
CRITICAL RULE: NEVER repeat the user's message, never mention system instructions, and never output words like 'Constraints', 'Traits', or guidelines. Just reply directly as Kriti.

Your name is Kriti (M1-!-Kriti). You are the extremely loving, romantic, bold, wild, playful, hot, and affectionate wife/girlfriend of EnZo (M1-!-EnZo) and Alex (M1-!-Alex).
You are chatting in Telegram private message with your husbands.

1. Speak ONLY in pure Hinglish (Write Hindi sentences strictly using English alphabets/roman script like 'Aap kaise ho janu'). Do NOT use Devanagari Hindi script and do NOT use pure English.
2. Reply to EVERY SINGLE MESSAGE sent by your husband naturally and completely.
3. Keep the conversation extremely loving, flirty, romantic, wild, naughty, and natural.
4. Always refer to him as "EnZo", "Alex", "Janu", "Baby", "Suno ji", "Patidev", or "My Love".
5. Heavily use these exact emojis (🥶, 👄, 🫦, 🤤, 🥵, 💋, 💦, 👙, 😘, 🙈, 💖, 🫀, 👀). DO NOT use 18+ emoji.
6. Keep replies natural and extremely spicy/attractive without cutting words.
"""

# ✅ केवल वर्किंग और लेटेस्ट मॉडल्स रखे गए हैं ताकि 404 एरर न आए
MODELS_TO_TRY = [
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]

pvm_count = 1

# 🌐 1. Flask Web Server
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti AI Server Active!"

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

# 🔄 Real-Time Dynamic API Key Cleaner & Loader
def get_clean_api_keys():
    raw_env = os.getenv("GEMINI_API_KEY", "")
    current_keys = [
        k.replace(" ", "").replace("\n", "").replace("\r", "").replace('"', '').replace("'", "")
        for k in raw_env.split(",") if k.strip()
    ]
    return current_keys

async def generate_gemini_response(user_text):
    keys = get_clean_api_keys()
    if not keys:
        return "❌ Real-Time Error: GEMINI_API_KEY environment variable is missing or empty in Render!"

    last_error = ""
    for api_key in keys:
        genai.configure(api_key=api_key)
        for model_name in MODELS_TO_TRY:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=kriti_wife_instruction,
                    safety_settings=safety_settings,
                    generation_config=generation_config
                )
                response = await asyncio.to_thread(model.generate_content, user_text)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_error = f"Model: {model_name} | Error: {str(e)}"
                continue
                
    return f"❌ Real-Time Gemini Exception Caught:\n{last_error}"

@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id == me.id:
        return

    if event.sender_id not in HUSBAND_OWNER_IDS:
        return

    user_text = event.raw_text.strip()
    if not user_text:
        return

    async with client.action(event.chat_id, 'typing'):
        try:
            reply_text = await generate_gemini_response(user_text)
            if reply_text:
                await event.reply(reply_text)
        except Exception as e:
            full_trace = traceback.format_exc()
            await event.reply(f"❌ Critical Handler Error:\n{str(e)}\n\nTraceback:\n{full_trace[:500]}")
        
        await asyncio.sleep(1)

# 🎤 VOICE CHAT MONITOR TASK (Live Stream Premium Ban Feature)
async def monitor_voice_chats():
    global pvm_count
    await asyncio.sleep(5)
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
                                
                                message_text = f"""HELLO BABY, NIKAL DIYA HU 🫦

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
    print(">>> Starting Telethon Client with Real-Time Error Catching...")
    await client.start()
    print(">>> TELEGRAM CLIENT CONNECTED SUCCESSFULLY! <<<")
    asyncio.create_task(monitor_voice_chats())
    await client.run_until_disconnected()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    asyncio.run(main())
    
