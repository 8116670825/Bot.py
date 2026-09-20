import os
import asyncio
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

API_ID = 32815595
API_HASH = "4f8710ec9e88946139ac688af9eb1f5b"
SESSION_STRING = os.getenv("SESSION_STRING")

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

async def monitor_voice_chats():
    global pvm_count
    await client.start()
    me = await client.get_me()
    
    while True:
        try:
            # ऑनर का नया/करेंट नाम हर बार लाइव फ़ेच करना
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
                                # यूज़र को तुरंत बैन करना
                                await client(EditBannedRequest(chat, user_id, BAN_RIGHTS))
                                
                                channel_title = chat.title if hasattr(chat, 'title') else "Private"
                                first_name = user.first_name if user.first_name else "N/A"
                                username = f"@{user.username}" if user.username else "None"
                                uid = user.id
                                
                                # नया स्टाइलिश मैसेज फ़ॉर्मेट
                                message_text = f"""HELLO **{owner_name}** BOSS,

╭━─━─━─〔 👑 **{channel_title}** 〕─━─━─━╮
┊ ⚔️ **{owner_name}**
╰━─━─━─━─━─━─━─━─━─━─━─━─━╯

┌───[ 🩸 **PVM USER #{pvm_count:02d}** ]
├── 👤 **Name ➔** {first_name}
├── 🔗 **User ➔** {username}
└── 🆔 **ID ➔** `{uid}`

❖━─━─━─━─━─━─━─━─━─━─━─━─━❖
💀 **USKA AUKAT USKO DIKHA DIYA GAYA HAI, {owner_name} BOSS!** ⚰️"""

                                # ओनर की ID पर सिंगल मैसेज भेजना
                                try:
                                    await client.send_message(OWNER_ID, message_text)
                                    pvm_count += 1  # अगले बंदे के लिए काउंटर बढ़ाना
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
    
