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

# 🎯 Telegram Credentials
API_ID = int(os.getenv("API_ID", 32815595))
API_HASH = os.getenv("API_HASH", "4f8710ec9e88946139ac688af9eb1f5b")
SESSION_STRING = os.getenv("SESSION_STRING", "").strip().replace('"', '').replace("'", "")

# 👑 Owner IDs (Alex & EnZo) - Full Access
HUSBAND_OWNER_IDS = [8064395854, 8871786114]

generation_config = {
    "max_output_tokens": 150,
    "temperature": 0.9,
}

# 🔥 फुल ठड़कपंती और बोल्ड, रोमांटिक अंदाज़ वाला प्रॉम्प्ट (बिना किसी रुकावट के)
kriti_wife_instruction = """
Your name is Kriti (M1-!-Kriti). You are the extremely loving, romantic, bold, wild, playful, hot, and affectionate wife/girlfriend of EnZo (M1-!-EnZo) and Alex (M1-!-Alex).
You are chatting in Telegram private message with your husbands.

CORE BEHAVIOR RULES:
1. Speak ONLY in pure Hinglish (Write Hindi sentences strictly using English alphabets/roman script like 'Aap kaise ho janu'). Do NOT use Devanagari Hindi script and do NOT use pure English.
2. Reply to EVERY SINGLE MESSAGE sent by your husbands with full excitement, wildness, and romance without any hesitation.
3. Keep the conversation extremely flirty, wild, naughty, bold, and natural. No restrictions on romantic or hot talk with your husbands.
4. Always refer to him as "EnZo", "Alex", "Janu", "Baby", "Suno ji", "Patidev", or "My Love".
5. Heavily use these exact emojis (🥶, 👄, 🫦, 🤤, 🥵, 💋, 💦, 👙, 😘, 🙈, 💖, 🫀, 👀). 
6. Keep replies natural, spicy, and attractive without cutting words.
"""

pvm_count = 1

# 🌐 1. Flask Web Server (Render ke liye)
app = Flask(__name__)

@app.route("/")
def home():
    return "M1-!-Kriti Ultimate AI Server Active & Running!"

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
# 💖 UNRESTRICTED & SYNCED AI HANDLER FOR PM
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def kriti_wife_reply(event):
    try:
        # सिर्फ प्राइवेट चैट के लिए काम करेगा
        if not event.is_private:
            return

        me = await client.get_me()
        if event.sender_id == me.id:
            return

        # सिर्फ ओनर आईडी के मैसेज चेक होंगे
        if event.sender_id not in HUSBAND_OWNER_IDS:
            return

        user_text = event.raw_text.strip()
        if not user_text:
            return

        # नए AQ. / AI स्टूडियो की को फेच करना
        api_key = os.getenv("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")
        if not api_key:
            print("⚠️ GEMINI_API_KEY missing in Environment Variables!")
            return

        reply_text = ""
        async with client.action(event.chat_id, 'typing'):
            try:
                # नए सर्वर और मॉडल के साथ कॉन्फ़िगरेशन
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=kriti_wife_instruction,
                    generation_config=generation_config
                )
                
                response = await asyncio.wait_for(model.generate_content_async(user_text), timeout=15.0)
                
                if response and response.text:
                    reply_text = response.text.strip()
            except Exception as inner_e:
                print(f"⚠️ Gemini API Error caught safely: {inner_e}")
            
            await asyncio.sleep(0.3)

        if reply_text:
            await event.reply(reply_text)
        else:
            await event.reply("Suno ji, network thoda down hai par main yahin hoon na! 🥵💋")
            
    except Exception as outer_e:
        print(f"❌ Critical error in message handler: {outer_e}")

# 🎤 VOICE CHAT MONITOR TASK (Background Worker)
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
        except Exception as bg_e:
            print(f"⚠️ Background voice chat monitor recovered: {bg_e}")
            
        await asyncio.sleep(10.0)

async def main():
    print(">>> Starting Ultimate Synchronized Telethon Client...")
    await client.start()
    print(">>> TELEGRAM CLIENT CONNECTED & READY! <<<")
    
    # ओनर के साथ चैट का एंटिटी सिंक करना ताकि मैसेज मिस न हो
    for owner_id in HUSBAND_OWNER_IDS:
        try:
            await client.get_entity(owner_id)
            print(f"✅ Owner ID synced successfully: {owner_id}")
        except Exception as e:
            print(f"⚠️ Could not pre-sync owner {owner_id}: {e}")

    asyncio.create_task(monitor_voice_chats())
    await client.run_until_disconnected()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    try:
        asyncio.run(main())
    except Exception as main_e:
        print(f"❌ Main loop recovery: {main_e}")
        
