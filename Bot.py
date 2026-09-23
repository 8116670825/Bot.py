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
API_ID = 32815595
API_HASH = "4f8710ec9e88946139ac688af9eb1f5b"

# स्क्रीनशॉट में दी गई आपकी Telegram Session String (अगर बदलनी हो तो यहाँ बदलें)
SESSION_STRING = os.getenv("SESSION_STRING", "AQ.Ab8RN6INrbOOaqZUo-u0ChlDOtbll_pTDOuTm4QcTZvBq6Pc7Q")

# आपकी Gemini API Key (स्क्रीनशॉट से)
GEMINI_API_KEY = "AQ.Ab8RN6INrbOOaqZUo-u0ChlDOtbll_pTDOuTm4QcTZvBq6Pc7Q"

# Gemini AI सेटअप और फ्लर्टी प्रॉम्प्ट
genai.configure(api_key=GEMINI_API_KEY)
system_instruction = """
You are a deeply loving, romantic, cute, and playful flirty partner. 
You are talking to your boyfriend/boss. 
Always reply in Hindi/Hinglish with a lot of cute emojis (❤️, 😘, 🙈, 💖, 🔥, ✨). 
Keep your replies short, natural, super flirty, and romantic like a loving couple. 
Never drop the character.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)
ai_chat = model.start_chat(history=[])

# Owner ID
OWNER_ID = 8064395854

# Counter
pvm_count = 1

app = Flask(__name__)

@app.route("/")
def home():
    return "Userbot is running actively with AI!"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

BAN_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
    send_polls=True,
    change_info=False,
    invite_users=False,
    pin_messages=False
)

# ==========================================
# 💋 1. AI UNLIMITED FLIRTY CHAT (ओनर के लिए)
# ==========================================
@client.on(events.NewMessage(from_users=OWNER_ID))
async def ai_flirty_chat(event):
    user_text = event.raw_text.strip()
    
    if user_text:
        try:
            # Gemini AI से Flirty रिप्लाई जनरेट करना
            response = ai_chat.send_message(user_text)
            reply_text = response.text
            
            await event.reply(reply_text)
        except Exception as e:
            print(f"AI Error: {e}")

# ==========================================
# 🎤 2. VOICE CHAT MONITORING TASK
# ==========================================
async def monitor_voice_chats():
    global pvm_count
    await client.start()
    me = await client.get_me()
    
    while True:
        try:
            try:
                owner_entity = await client.get_entity(OWNER_ID)
                owner_name = owner_entity.first_name if owner_entity.first_name else "BOSS"
            except Exception:
                owner_name = "BOSS"

            async for dialog in client.iter_dialogs(limit=3):
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
                        call=call,
                        ids=[],
                        sources=[],
                        offset='',
                        limit=100
                    ))
                    
                    for participant in call_participants.participants:
                        try:
                            user_id = participant.peer.user_id
                        except AttributeError:
                            continue
                        
                        if user_id in admins:
                            continue
                        
                        try:
                            user = await client.get_entity(user_id)
                            if user.bot:
                                continue
                                
                            is_premium = getattr(user, "premium", False) or getattr(user, "emoji_status", None) is not None
                            
                            if is_premium:
                                await client(EditBannedRequest(chat, user_id, BAN_RIGHTS))
                                
                                channel_title = chat.title if hasattr(chat, 'title') else "Private"
                                first_name = user.first_name if user.first_name else "N/A"
                                username = f"@{user.username}" if user.username else "None"
                                uid = user.id
                                
                                message_text = f"""𝐇𝐄𝐋𝐋𝐎 ♡ {owner_name} 𝐁𝐎𝐒𝐒 🫩
❖──────────────────────❖
       [ 🩸 𝐃𝐄𝐀𝐓𝐇 𝐍𝐎𝐓𝐄 𝐋𝐈𝐒𝐓 #{pvm_count:02d} 🩸 
         📌 𝐍𝐚𝐦𝐞 ➔ {first_name} 📍
         📌 𝐔𝐬𝐞𝐫 ➔ {username} 📍
         📌 𝐈𝐃 ➔ `{uid}` 📍]
❖──────────────────────❖
💀 {channel_title} 𝐃𝐄𝐀𝐓𝐇 𝐍𝐎𝐓𝐄 ☠"""

                                try:
                                    await client.send_message(OWNER_ID, message_text)
                                    pvm_count += 1
                                except Exception:
                                    pass

                        except Exception:
                            pass
                                
                except Exception:
                    continue
                    
        except Exception:
            pass
            
        await asyncio.sleep(0.05)

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
                                    
