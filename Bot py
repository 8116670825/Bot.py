import os
from telethon import TelegramClient, events
from flask import Flask

# Flask ऐप रेंडर (Render) को जिंदा रखने के लिए
app = Flask('')

@app.route('/')
def home():
    return "Userbot is running!"

def run():
    app.run(host='0.5.0.0', port=int(os.environ.get('PORT', 8080)))

# क्रेडेंशियल्स
api_id = 32815595
api_hash = '4f8710ec9e88946139ac688af9eb1f5b'
session_string = os.environ.get('SESSION_STRING')

client = TelegramClient(StringSession(session_string), api_id, api_hash)

# वॉयस चैट में प्रीमियम यूजर को बैन करने का लॉजिक
@client.on(events.ChatAction)
async def handler(event):
    if event.user_joined or event.user_added:
        user = await event.get_user()
        # यदि यूजर प्रीमियम है (ध्यान दें: टेलीथॉन में प्रीमियम चेक करने का तरीका)
        if getattr(user, 'premium', False):
            try:
                # वॉयस चैट / ग्रुप से बैन करना
                await client.edit_admin(event.chat_id, user.id, ban_users=True)
                print(f"Banned premium user: {user.id}")
            except Exception as e:
                print(f"Error banning user: {e}")

if __name__ == '__main__':
    import threading
    from telethon.sessions import StringSession
    
    t = threading.Thread(target=run)
    t.start()
    
    client.start()
    client.run_until_disconnected()
