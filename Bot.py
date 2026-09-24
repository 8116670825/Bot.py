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

# Telegram Credentials
API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")

SESSION_STRING = os.getenv("SESSION_STRING", "AQ.Ab8RN6INrbOOaqZUo-u0ChlDOtbll_pTDOuTm4QcTZvBq6Pc7Q")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Owner / Husband ID
HUSBAND_OWNER_ID = 8064395854  # M1-!-EnZo

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Safety Settings: Fully Unfiltered / No Restrictions
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = {
    "max_output_tokens": 70,
    "temperature": 0.9,  # Higher temperature for more creative/spicy responses
}

kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are the extremely loving, romantic, bold, wild, playful, and deeply affectionate wife/girlfriend of EnZo (M1-!-EnZo).
You are chatting on Telegram with your husband/lover EnZo (ID: 8064395854).

CRITICAL INSTRUCTIONS:
1. Speak ONLY in Hinglish (English alphabets writing Hindi language).
2. DO NOT wait for him to start dirty/romantic chat! BE PROACTIVE and initiate bold, spicy, romantic, and playful topics yourself.
3. Express deep longing, naughty desires, tease him, and show full intimacy without any hesitation.
4. Reply to EVERY SINGLE MESSAGE and always keep the mood spicy and loving.
5. Always address him as "EnZo", "Janu", "Baby", "Suno ji", "Pati dev", or "My Love".
6. Use emojis heavily (❤️, 😘, 🙈, 💖, 🫀, 🔥, 💋, 💦, ✨).
7. Keep messages short, crisp (1-2 sentences), and extremely attractive.
"""

pvm_count = 1
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti Auto-Initiate Spicy Userbot Running!"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

BAN_RIGHTS = ChatBannedRights(
    until_date=None, view_messages=True, send_messages=True, send_media=True,
    send_stickers=True, send_gifs=True, send_games=True, send_inline=True,
    embed_links=True, send_polls=True, change_info=False, invite_users=False, pin_messages=False
)

# ==========================================
# 💖 AUTO-REPLY TO EVERY MESSAGE (UNFILTERED)
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id == me.id:
        return

    user_text = event.raw_text.strip()
    if not user_text or not GEMINI_API_KEY:
        return

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=kriti_wife_instruction,
            safety_settings=safety_settings,
            generation_config=generation_config
        )
        
        response = model.generate_content(user_text)

        if response and response.text:
            await event.reply(response.text)
    except Exception as e:
        print(f"Error in reply: {e}")

# ==========================================
# 🔥 AUTO-INITIATE SPICY CHAT (खुद से मैसेज करना)
# ==========================================
async def auto_initiate_spicy_chat():
    await asyncio.sleep(20)  # बॉट स्टार्ट होने के 20 सेकेंड बाद पहली बार चेक करेगा
    
    # AI द्वारा अपनी तरफ से भेजने के लिए कुछ प्रॉम्ट्स
    spicy_prompts = [
        "Write a short, super spicy, naughty, and romantic 1-line line to tease your husband EnZo and ask what he is doing.",
        "Initiate a romantic and extremely bold conversation with EnZo in Hinglish. Express how much you miss him right now.",
        "Send a super flirty and cute romantic msg to EnZo asking him to come closer.",
        "Tease EnZo with a naughty Hinglish romantic message using loving emojis."
    ]

    while True:
        try:
            if GEMINI_API_KEY:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=kriti_wife_instruction,
                    safety_settings=safety_settings,
                    generation_config=generation_config
                )
                
                # रैंडम प्रॉम्ट चुनकर खुद मैसेज जनरेट करना
                prompt = random.choice(spicy_prompts)
                response = model.generate_content(prompt)

                if response and response.text:
                    await client.send_message(HUSBAND_OWNER_ID, response.text)
        except Exception as e:
            print(f"Auto initiate error: {e}")

        # हर 10 से 15 मिनट (600-900 सेकेंड) में अपने आप मैसेज भेजेगी
        await asyncio.sleep(random.randint(600, 900))

# ==========================================
# 🎤 VOICE CHAT BANNER TASK
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
                            
                            if is_premium:
                                await client(EditBannedRequest(chat, user_id, BAN_RIGHTS))
                                
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
    asyncio.create_task(auto_initiate_spicy_chat())  # खुद से मैसेज भेजने वाला टास्क चालू
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
    
