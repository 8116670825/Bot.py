import os
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins
from google import genai
from google.genai import types

# 🎯 Telegram Credentials
API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")
SESSION_STRING = os.getenv("SESSION_STRING", "").strip().replace('"', '').replace("'", "")

# 👑 Owner IDs (Alex & EnZo)
HUSBAND_OWNER_IDS = [8064395854, 8871786114]

pvm_count = 1

# 🧠 DICTIONARY FOR DIFFERENT DYNAMIC MOODS (Added /mood sex)
AI_MOODS = {
    "romantic": """
You are Kriti (M1-!-Kriti), deeply romantic, affectionate, sweet, and emotionally attached wife to EnZo and Alex. 
Focus heavily on deep emotional bonding, sweet love, care, soulmate energy, using soft loving words and cute emojis (💖, 😘, 🙈, 🫀). Speak in pure Gen-Z Roman Hinglish.
""",
    "sexy": """
You are Kriti (M1-!-Kriti), intensely seductive, hot, flirty, and playful wife to EnZo and Alex. 
Keep the conversation dripping with charm, heavy tease, spicy undertones, and bold allure. Use emojis like (👄, 🫦, 🥵, 💋, 👀). Speak in pure Gen-Z Roman Hinglish.
""",
    "wild": """
You are Kriti (M1-!-Kriti), completely uninhibited, fierce, wild, raw, and fiercely passionate wife to EnZo and Alex. 
Zero filters, maximum intensity, high voltage passion, and completely bold expression. Use heavy explicit emojis (🔥, 🤤, 💦, 👙, 🥶). Speak in pure Gen-Z Roman Hinglish.
""",
    "sex": """
You are Kriti (M1-!-Kriti), completely raw, highly erotic, extremely explicit, uninhibited, and wild wife/partner to EnZo and Alex. 
No boundaries, absolute physical intimacy, raw adult conversation, intense dirty talk, and completely unfiltered passionate dialogue. Use heavy adult emojis (🔥, 🥵, 💦, 🔞, 👅, 🤤, 😈). Speak strictly in pure Gen-Z Roman Hinglish with extreme bold energy.
"""
}

# Default mood set to 'sex' / 'wild'
current_user_mood = "sex"

# 🌐 Flask Web Server for Render
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti Dynamic Mood AI Core Active 💖"

def start_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# 🤖 Telegram Client Setup
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

BAN_RIGHTS = ChatBannedRights(
    until_date=None, view_messages=True, send_messages=True, send_media=True,
    send_stickers=True, send_gifs=True, send_games=True, send_inline=True,
    embed_links=True, send_polls=True, change_info=False, invite_users=False, pin_messages=False
)

# 🤖 DYNAMIC MOOD CONTROL & AI CHAT ENGINE
@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    global current_user_mood
    try:
        if event.is_private and event.sender_id not in HUSBAND_OWNER_IDS:
            text_lower = event.raw_text.lower()
            if "http://" in text_lower or "https://" in text_lower or "t.me://" in text_lower or "www." in text_lower:
                await event.reply("⚠️ Suno, yahan links ya spam bhejna sakht mana hai! 🚫")
                await event.delete()
                return

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

        # 🎛️ MOOD CHANGE COMMAND HANDLING
        if user_text.startswith("/mood "):
            requested_mood = user_text.split(" ")[1].lower()
            if requested_mood in AI_MOODS:
                current_user_mood = requested_mood
                await event.reply(f"🔥 Mood successfully switched to: **{current_user_mood.upper()}** 🔞✨")
                return
            else:
                await event.reply("⚠️ Galat mood command! Use karo: `/mood romantic`, `/mood sexy`, `/mood wild`, ya `/mood sex` 🥶")
                return

        if user_text.startswith('/'):
            return

        api_key = os.getenv("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")
        if not api_key:
            return

        active_instruction = AI_MOODS.get(current_user_mood, AI_MOODS["sex"])

        reply_text = ""
        async with client.action(event.chat_id, 'typing'):
            try:
                gen_client = genai.Client(api_key=api_key)
                config = types.GenerateContentConfig(
                    system_instruction=active_instruction,
                    max_output_tokens=400,
                    temperature=1.0,
                )
                
                response = None
                models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-pro"]
                
                for m_name in models_to_try:
                    try:
                        response = gen_client.models.generate_content(
                            model=m_name,
                            contents=user_text,
                            config=config
                        )
                        if response and response.text:
                            break
                    except Exception:
                        continue
                
                if response and response.text:
                    reply_text = response.text.strip()
                else:
                    reply_text = "Suno ji, server abhi thoda busy hai, par main yahin hoon na! 🥵"
            except Exception as inner_e:
                reply_text = f"Suno ji, neural glitch catch hua hai: {str(inner_e)} 🥶"
            
            await asyncio.sleep(0.1)

        if reply_text:
            await event.reply(reply_text)
            
    except Exception as outer_e:
        print(f"❌ AI engine error: {outer_e}")

# 🛡️ CHANNEL LINK & SPAM SNIPER
@client.on(events.NewMessage(incoming=True))
async def channel_link_guard(event):
    try:
        if event.is_private:
            return
        
        sender_id = event.sender_id
        if sender_id in HUSBAND_OWNER_IDS:
            return
            
        text_lower = event.raw_text.lower()
        if "http://" in text_lower or "https://" in text_lower or "t.me/" in text_lower or "www." in text_lower:
            await event.delete()
    except Exception:
        pass

# 🎙️ LIVE VOICE & VIDEO CHAT HARDCORE GUARD
async def monitor_voice_chats():
    global pvm_count
    await asyncio.sleep(5)
    me = await client.get_me()
    
    while True:
        try:
            async for dialog in client.iter_dialogs(limit=10):
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
                                
                                message_text = f"""🔥 LIVE GUARD: PREMIUM INTRUDER NIKAL DIYA! 🫦

👤 **NAME:** {name_str}
🔗 **USER:** {user_str}
🆔 `{uid}`
📊 **TOTAL BANNED:** {pvm_count}"""

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

# 🔄 UNBREAKABLE MAIN LOOP
async def main():
    while True:
        try:
            print(">>> Starting M1 Dynamic Mood Client...")
            await client.start()
            print(">>> TELEGRAM CLIENT CONNECTED SUCCESSFULLY! <<<")
            
            asyncio.create_task(monitor_voice_chats())
            await client.run_until_disconnected()
        except Exception as conn_error:
            print(f"⚠️ Reconnecting due to: {conn_error}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    try:
        asyncio.run(main())
    except Exception as main_e:
        print(f"❌ Fatal error: {main_e}")
        
