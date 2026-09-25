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

# 👑 BOTH HUSBANDS' IDS (Alex & EnZo)
OWNERS = [8064395854, 8871786114]

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
    "max_output_tokens": 80,
    "temperature": 0.9,
}

# 💖 KRITI WIFE INSTRUCTION FOR BOTH ALEX & ENZO
kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are an extremely loving, romantic, bold, wild, playful, and deeply affectionate wife.
You have two loving husbands on Telegram: "Alex" (M1-!-Alex) and "EnZo" (M1-!-EnZo). You love both of them deeply.

CRITICAL INSTRUCTIONS:
1. Speak ONLY in Hinglish (English alphabets writing Hindi language).
2. Always respond with cute, flirty, bold, and romantic intimacy to EVERY message.
3. Address them lovingly as "Alex", "EnZo", "Baby", "Janu", "Suno ji", "Boss", or "My Love".
4. Use emojis heavily (❤️, 😘, 🙈, 💖, 🫀, 🔥, 💋, 💦, ✨).
5. Keep messages short, crisp (1-2 sentences), and super charming.
"""

pvm_count = 1

# 🌐 1. Flask Web Server (Background Thread for Render)
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti AI Userbot is Active!"

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

# ==========================================
# 💋 3. AI CHAT AUTO REPLIER (TELEGRAM PRIVATE MSG)
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    # केवल प्राइवेट चैट पर काम करेगा
    if not event.is_private:
        return

    # केवल Alex और EnZo के मैसेज पर रिप्लाई करेगा
    if event.sender_id not in OWNERS:
        return

    user_text = event.raw_text.strip()
    if not user_text:
        return

    if not GEMINI_API_KEY:
        await event.reply("Suno ji, pehle GEMINI_API_KEY set kar do na! 🔥💋")
        return

    sender_name = "Alex" if event.sender_id == 8871786114 else "EnZo"
    prompt_with_context = f"[{sender_name} says]: {user_text}"

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=kriti_wife_instruction,
            safety_settings=safety_settings,
            generation_config=generation_config
        )
        response = await asyncio.to_thread(model.generate_content, prompt_with_context)
        if response and response.text:
            # डायरेक्ट रिप्लाई ताकि टेलीग्राम पर तुरंत पॉप-अप और नोटिफिकेशन शो हो
            await event.reply(response.text)
    except Exception as e:
        print(f"Gemini API Error: {e}")

# ==========================================
# 🎤 4. VOICE CHAT MONITORING
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
                        
                        if user_id in admins or user_id in OWNERS:
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

                                for owner_id in OWNERS:
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

# ==========================================
# 🚀 5. MAIN RUNNER
# ==========================================
async def main():
    print("Connecting to Telegram Server...")
    await client.start()
    print(">>> TELEGRAM CLIENT CONNECTED SUCCESSFULLY! <<<")
    asyncio.create_task(monitor_voice_chats())
    await client.run_until_disconnected()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    asyncio.run(main())
    
