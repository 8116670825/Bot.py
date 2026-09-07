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
    await client.start()
    print("Userbot started successfully and scanning channel live streams...")
    
    while True:
        try:
            async for dialog in client.iter_dialogs():
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
                            if user.bot or user.id == (await client.get_me()).id:
                                continue
                                
                            # Check standard premium OR hidden/custom emoji status
                            is_premium = getattr(user, "premium", False) or getattr(user, "emoji_status", None) is not None
                            
                            if is_premium:
                                await client(EditBannedRequest(chat, user_id, BAN_RIGHTS))
                                print(f"SUCCESS: Banned Premium user {user_id} in live stream of {chat.title}")
                        except Exception as e:
                            print(f"Error processing user {user_id}: {e}")
                                
                except Exception as inner_e:
                    continue
                    
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            
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
    
