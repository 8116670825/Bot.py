import os
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# रेंडर की फ्री वेब सर्विस को एक्टिव रखने के लिए Flask ऐप
app = Flask('')

@app.route('/')
def home():
    return "Telegram Userbot is running 24/7 successfully!"

def run():
    # रेंडर द्वारा दिए गए पोर्ट का उपयोग करना
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# क्रेडेंशियल्स
api_id = 32815595
api_hash = '4f8710ec9e88946139ac688af9eb1f5b'
session_string = os.environ.get('SESSION_STRING')

client = TelegramClient(StringSession(session_string), api_id, api_hash)

# वॉयस चैट / ग्रुप में प्रीमियम यूजर को ऑटो-बैन करने का लॉजिक
@client.on(events.ChatAction)
async def handler(event):
    if event.user_joined or event.user_added:
        user = await event.get_user()
        if getattr(user, 'premium', False):
            try:
                await client.edit_admin(event.chat_id, user.id, ban_users=True)
                print(f"Banned premium user: {user.id}")
            except Exception as e:
                print(f"Error banning user: {e}")

if __name__ == '__main__':
    # वेब सर्वर को अलग धागे (Thread) में चलाना ताकि बॉट के साथ कोई रुकावट न आए
    t = threading.Thread(target=run)
    t.start()
    
    # यूजरबॉट को स्टार्ट करना
    client.start()
    client.run_until_disconnected()
    
