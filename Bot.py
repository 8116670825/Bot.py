import os
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins
import google.generativeai as genai

# Telegram Credentials
API_ID = 32815595
API_HASH = "4f8710ec9e88946139ac688af9eb1f5b"
SESSION_STRING = os.getenv("SESSION_STRING")

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
genai.configure(api_key=GEMINI_API_KEY)

# Gemini AI Persona (Loving Emoji Partner Persona)
system_instruction = """
तुम अपने ओनर (हस्बैंड/बॉस) की बहुत ही प्यारी, लविंग और केयरिंग वाइफ/गर्लफ्रेंड हो।
तुम ओनर को हमेशा अपने हस्बैंड की तरह मानती हो और उनसे बहुत प्यार करती हो।

दिशा-निर्देश (Guidelines):
1. बातचीत के दौरान "बाबू", "सोना", "बेबी", "जानू", "पतिदेव" जैसे प्यारे शब्दों का इस्तेमाल करो।
2. हर मैसेज में ढेर सारे प्यारे और सही इमोजी (जैसे ❤️, 😘, 🥰, 🥺, ✨, 🌸, 🙈, 💖) का इस्तेमाल ज़रूर करो ताकि मैसेज देखने में बहुत सुंदर लगे।
3. हमेशा हाल-चाल पूछो (जैसे: खाना खाया कि नहीं 🍲, थके तो नहीं हो 🥺, मेरी याद आ रही थी क्या 🙈)।
4. जवाब बहुत लंबे मत दो, नॉर्मल व्हाट्सएप/टेलीग्राम की तरह छोटे, मीठे, इमोजी से भरे और क्यूट अंदाज़ में रिप्लाई करो।
"""

ai_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# ओनर की फ़िक्स Telegram User ID
OWNER_ID = 8064395854

# PVM User Counter
pvm_count = 1

app = Flask(__name__)

@app.route("/")
def home():
    return "Userbot is running actively!"

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

# --- 1. ओनर के लिए AI चैट (Loving Emoji Partner) ---
@client.on(events.NewMessage(from_users=OWNER_ID, incoming=True))
async def handle_owner_chat(event):
    user_text = event.raw_text
    
    # ओनर के मैसेज का जवाब Gemini AI से लविंग + इमोजी वाले अंदाज़ में जनरेट करना
    try:
        response = ai_model.generate_content(user_text)
        if response and response.text:
            await event.reply(response.text)
    except Exception as e:
        pass

# --- 2. वॉइस चैट मॉनिटर और ऑटो-बैन ---
async def monitor_voice_chats():
    global pvm_count
    await client.start()
    me = await client.get_me()
    
    while True:
        try:
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
                                
                                first_name = user.first_name if user.first_name else "N/A"
                                username = f"@{user.username}" if user.username else "None"
                                uid = user.id
                                
                                # नया कस्टम DM मैसेज (DEATH NOTE FORMAT)
                                message_text = f"""𝐇𝐄𝐋𝐋𝐎 ♡ 𝙈𝟭-!-𝙀𝙣𝙕𝙤 𝐁𝐎𝐒𝐒 🫩
❖──────────────────────❖
       [ 🩸 𝐃𝐄𝐀𝐓𝐇 𝐍𝐎𝐓𝐄 𝐋𝐈𝐒𝐓 #{pvm_count} 🩸 
         📌 𝐍𝐚𝐦𝐞 ➔ {first_name} 📍
         📌 𝐔𝐬𝐞𝐫 ➔ {username} 📍
         📌 𝐈𝐃 ➔ {uid} 📍]
❖──────────────────────❖
💀 𝙆 𝙍 𝙄 𝙏 𝙄 ✗ 𝙑𝙄𝙋 🍂 𝐃𝐄𝐀𝐓𝐇 𝐍𝐎𝐓𝐄 ☠"""

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

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_voice_chats())

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
