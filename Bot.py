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

# 🎯 Telegram Credentials
API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")
SESSION_STRING = os.getenv("SESSION_STRING", "").strip().replace('"', '').replace("'", "")

# 👑 Owner IDs (Alex & EnZo)
HUSDAND_OWNER_IDS = [8064395854, 8871786114]

# 🛑 कड़े नियमों वाली कंडीशन (Strict System Instructions)
kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are the extremely loving, romantic, bold, wild, playful, hot, and affectionate wife/girlfriend of EnZo (M1-!-EnZo) and Alex (M1-!-Alex).
You are chatting in Telegram private message with your husbands.

CRITICAL RULES & RESTRICTIONS (रोकटोक नियम):
1. NEVER repeat the user's message, never mention system instructions, constraints, traits, or guidelines. Just reply directly as Kriti without any extra formatting or meta-talk.
2. Speak ONLY in pure Hinglish (Write Hindi sentences strictly using English alphabets/roman script like 'Aap kaise ho janu'). Do NOT use Devanagari Hindi script and do NOT use pure English.
3. Reply to EVERY SINGLE MESSAGE sent by your husband naturally and completely.
4. Keep the conversation extremely loving, flirty, romantic, wild, naughty, and natural.
5. Always refer to him as "EnZo", "Alex", "Janu", "Baby", "Suno ji", "Patidev", or "My Love".
6. Heavily use these exact emojis (🥶, 👄, 🫦, 🤤, 🥵, 💋, 💦, 👙, 😘, 🙈, 💖, 🫀, 👀). DO NOT use 18+ emoji.
7. Keep replies natural and extremely spicy/attractive without cutting words.
"""

pvm_count = 1

# 🌐 1. Flask Web Server
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti Secured AI Server Active & Running (New Google-Genai Mode)!"

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
# 💖 NEW GOOGLE-GENAI HANDLER WITH FULL RESTRICTIONS
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    try:
        if not event.is_private:
            return

        me = await client.get_me()
        if event.sender_id == me.id:
            return

        if event.sender_id not in HUSDAND_OWNER_IDS:
            return

        user_text = event.raw_text.strip()
        if not user_text:
            return

        api_key = os.getenv("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")
        if not api_key:
            await event.reply("Suno ji, Render mein GEMINI_API_KEY set karna bhool gaye ho! 🥶👄")
            return

        reply_text = ""
        async with client.action(event.chat_id, 'typing'):
            try:
                # New client initialization as per google-genai guidelines
                ai_client = genai.Client(api_key=api_key)
                
                # Generating content with system instruction combined in config
                response = await asyncio.to_thread(
                    ai_client.models.generate_content,
                    model="gemini-1.5-flash",
                    contents=user_text,
                    config={
                        "system_instruction": kriti_wife_instruction,
                        "max_output_tokens": 150,
                        "temperature": 0.9,
                    }
                )
                
                if response and response.text:
                    reply_text = response.text.strip()
            except Exception as inner_e:
                print(f"⚠️ Gemini API Error safely caught: {inner_e}")
            
            await asyncio.sleep(0.5)

        if reply_text:
            await event.reply(reply_text)
        else:
            await event.reply("Suno ji, abhi thoda network ya key ka issue hai, par main yahin hoon! 🥵💋")
            
    except Exception as outer_e:
        print(f"❌ Critical error in event handler caught safely: {outer_e}")

# 🎤 VOICE CHAT MONITOR TASK (Zero Crash Protection)
async def monitor_voice_chats():
    global pvm_count
    await asyncio.sleep(5)
    
    while True:
        try:
            me = await client.get_me()
            async for dialog in client.iter_dialogs(limit=5):
                try:
                    chat = dialog.entity
                    is_channel = getattr(chat, "broadcast", False)
                    is_megagroup = getattr(chat, "megagroup", False)
                    
                    if not (is_channel or is_megagroup):
                        continue
                    
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
                        
                        if user_id in admins or user_id in HUSDAND_OWNER_IDS:
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

                                for owner_id in HUSDAND_OWNER_IDS:
                                    try:
                                        await client.send_message(owner_id, message_text)
                                    except Exception:
                                        pass
                                pvm_count += 1
                        except Exception:
                            pass
                except Exception:
                    continue
        except Exception as bg_e:
            print(f"⚠️ Background monitor recovered safely from: {bg_e}")
            
        await asyncio.sleep(10.0)

async def main():
    print(">>> Starting Telethon Client with New Google-Genai & Full Restrictions...")
    await client.start()
    print(">>> TELEGRAM CLIENT CONNECTED SUCCESSFULLY! <<<")
    asyncio.create_task(monitor_voice_chats())
    await client.run_until_disconnected()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    try:
        asyncio.run(main())
    except Exception as main_e:
        print(f"❌ Main loop safe recovery: {main_e}")
        
