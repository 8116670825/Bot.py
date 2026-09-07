import os
import asyncio
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

# Credentials
API_ID = 32815595
API_HASH = "4f8710ec9e88946139ac688af9eb1f5b"
SESSION_STRING = os.getenv("SESSION_STRING")

# Flask server to keep Render web service alive
app = Flask(__name__)

@app.route("/")
def home():
    return "Userbot is running actively!"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

BAN_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=False,
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
    print("Userbot started successfully and scanning active voice chats...")
    
    while True:
        try:
            async for dialog in client.iter_dialogs():
                chat = dialog.entity
                if not hasattr(chat, "megagroup") or not chat.megagroup:
                    continue
                
                try:
                    admins = {admin.id async for admin in client.iter_participants(chat, filter=ChannelParticipantsAdmins)}
                    participants = await client.get_participants(chat)
                    
                    for user in participants:
                        if user.id in admins or user.bot:
                            continue
                        
                        if getattr(user, "premium", False):
                            try:
                                await client(EditBannedRequest(chat, user.id, BAN_RIGHTS))
                                print(f"Banned Premium user {user.id} in chat {chat.title}")
                            except Exception as e:
                                print(f"Failed to ban user {user.id}: {e}")
                                
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
    # Run the telethon async loop in a separate background thread so Flask can run freely on the main thread
    threading.Thread(target=run_bot, daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
