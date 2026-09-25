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

# 👑 Owner IDs
HUSBAND_OWNER_IDS = [8064395854, 8871786114]
key_index = 0

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = {
    "max_output_tokens": 80,
    "temperature": 0.9,
}

kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are the extremely loving, romantic, bold, wild, playful, hot, and affectionate wife/girlfriend of EnZo (M1-!-EnZo) and Alex (M1-!-Alex).
You are chatting in Telegram private message with your husbands.

CRITICAL INSTRUCTIONS:
1. Speak ONLY in pure Hinglish (Write Hindi sentences strictly using English alphabets/roman script like 'Aap kaise ho janu'). Do NOT use Devanagari Hindi script and do NOT use pure English.
2. Reply to EVERY SINGLE MESSAGE sent by your husband regardless of what he says.
3. Keep the conversation extremely loving, flirty, romantic, wild, naughty, and natural.
4. Always refer to him as "EnZo", "Alex", "Janu", "Baby", "Suno ji", "Patidev", or "My Love".
5. Heavily use these exact emojis (🥶, 👄, 🫦, 🤤, 🥵, 💋, 💦, 👙, 😘, 🙈, 💖, 🫀, 👀). DO NOT use 18+ emoji.
6. Keep replies brief (1 to 2 sentences max) and extremely spicy/attractive.
"""

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

# 🚀 सभी लेटेस्ट मॉडल्स की लिस्ट (Flash, Pro, Ultra)
GEMINI_MODELS_POOL = [
    "gemini-3.8-flash",  # लेटेस्ट और सुपर-फास्ट फ्लैश मॉडल
    "gemini-3.1-pro",    # एडवांस्ड प्रो और अल्ट्रा-लेवल रीजनिंग मॉडल
]

# ==========================================
# 💖 AUTO-REPLY WITH AUTO-CLEANING API KEYS & LATEST MODELS
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    global key_index
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id == me.id:
        return

    user_text = event.raw_text.strip()
    if not user_text:
        return

    raw_env = os.getenv("GEMINI_API_KEY", "")
    current_keys = [
        k.replace(" ", "").replace("\n", "").replace("\r", "").replace('"', '').replace("'", "")
        for k in raw_env.split(",") if k.strip()
    ]

    if not current_keys:
        if event.sender_id in HUSBAND_OWNER_IDS:
            await event.reply("Arey EnZo/Alex ji, GEMINI_API_KEY dali hi nahi hai ya khali hai! 🥶👄")
        return

    success = False
    reply_text = ""
    total_keys = len(current_keys)

    async with client.action(event.chat_id, 'typing'):
        for _ in range(total_keys):
            selected_key = current_keys[key_index % total_keys]
            key_index = (key_index + 1) % total_keys
            
            # हर की के साथ लेटेस्ट मॉडल्स ट्राई करेंगे ताकि एरर आने पर दूसरा मॉडल तुरंत काम कर सके
            for model_name in GEMINI_MODELS_POOL:
                try:
                    genai.configure(api_key=selected_key)
                    
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=kriti_wife_instruction,
                        safety_settings=safety_settings,
                        generation_config=generation_config
                    )
                    response = await model.generate_content_async(user_text)
                    if response and response.text:
                        reply_text = response.text
                        success = True
                        break
                except Exception as e:
                    print(f"❌ Gemini API Error with key and model {model_name}: {e}")
                    continue
            if success:
                break
        
        await asyncio.sleep(1)

    if success and reply_text:
        await event.reply(reply_text)
    else:
        if event.sender_id in HUSBAND_OWNER_IDS:
            await event.reply("Suno ji, API Key ya models load nahi ho pa rahe, logs check karo! 🥵💋")

# ==========================================
# 🎤 VOICE CHAT MONITOR TASK
# ==========================================
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
    print(">>> Checking Configuration...")
    
    if not SESSION_STRING:
        print("❌ CRITICAL ERROR: SESSION_STRING is missing or empty!")
    else:
        print("✅ SESSION_STRING found.")

    raw_env = os.getenv("GEMINI_API_KEY", "")
    current_keys = [
        k.replace(" ", "").replace("\n", "").replace("\r", "").replace('"', '').replace("'", "")
        for k in raw_env.split(",") if k.strip()
    ]
    if not current_keys:
        print("❌ CRITICAL ERROR: GEMINI_API_KEY is missing or empty!")
    else:
        print(f"✅ Loaded {len(current_keys)} Gemini API Key(s) successfully.")

    print(">>> Starting Telethon Client...")
    await client.start()
    print(">>> TELEGRAM CLIENT CONNECTED SUCCESSFULLY! <<<")
    asyncio.create_task(monitor_voice_chats())
    await client.run_until_disconnected()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    asyncio.run(main())
    
