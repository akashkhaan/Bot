import telebot
import requests
import threading
import time
from pytube import YouTube
import os

BOT_TOKEN = "8200935468:AAHc7xOVyYk35xQlDAURdr0jFxaULtQNGh8"
API_KEY = "c8WRmO3Z0h79o4Vq2ENbMYtgFKnLrfPA65vkaGdXTlDiCHsI1QkVYeBC8RJXNiqPTQZbImFzEjtKWcaG"

CHANNEL = "@techtrickindia"
YOUTUBE_LINK = "https://youtube.com/@techtrickindia9?si=Rpy7JUHkD24g2c0W"
AUTO_MSG_BOT = "https://t.me/techtricksmsbot"
ADMIN_SUPPORT = "https://t.me/TechTrickIndia3"
CHANNEL_LINK = "https://t.me/TechTrickIndia"

bot = telebot.TeleBot(BOT_TOKEN)

# -------- AUTO STORAGE --------
auto_senders = {}

# -------- JOIN CHECK --------
def joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member","administrator","creator"]
    except:
        return False

# -------- START --------
@bot.message_handler(commands=['start'])
def start(message):

    if not joined(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📺 YouTube Subscribe", url=YOUTUBE_LINK))
        markup.add(telebot.types.InlineKeyboardButton("🤖 Automatic Message Bot", url=AUTO_MSG_BOT))
        markup.add(telebot.types.InlineKeyboardButton("👨‍💻 Contact Admin Support", url=ADMIN_SUPPORT))
        markup.add(telebot.types.InlineKeyboardButton("🔥 Join Channel", url=CHANNEL_LINK))
        markup.add(telebot.types.InlineKeyboardButton("✅ VERIFY", url=CHANNEL_LINK))

        bot.send_message(
            message.chat.id,
            "🚫 Bot use karne se pehle:\n\n"
            "1️⃣ YouTube channel subscribe karo\n"
            "2️⃣ Telegram channel join karo\n"
            "3️⃣ VERIFY button dabao",
            reply_markup=markup
        )
        return

    bot.send_message(message.chat.id,"✅ Access Granted! Ab bot use kar sakte ho.")

# -------- SMS COMMAND --------
@bot.message_handler(commands=['sms'])
def sms(message):

    if not joined(message.from_user.id):
        bot.reply_to(message,"❌ Pehle verification complete karo /start")
        return

    try:
        data = message.text.split(" ",2)
        number = data[1]
        msg = data[2]

        requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            json={
                "sender_id":"FSTSMS",
                "message":msg,
                "language":"english",
                "route":"q",
                "numbers":number
            },
            headers={"authorization":API_KEY}
        )

        bot.reply_to(message,"✅ SMS Sent Successfully!")

    except:
        bot.reply_to(message,"Use:\n/sms number message")

# ===============================
# 🔥 AUTO MESSAGE SYSTEM
# ===============================
def auto_send(chat_id, text, delay):
    while auto_senders.get(chat_id):
        try:
            bot.send_message(chat_id, text)
            time.sleep(delay)
        except:
            break

# -------- AUTO START --------
@bot.message_handler(commands=['auto'])
def auto(message):

    if not joined(message.from_user.id):
        bot.reply_to(message,"❌ Pehle verification complete karo /start")
        return

    try:
        data = message.text.split(" ",2)
        delay = int(data[1])   # seconds
        text = data[2]
        chat_id = message.chat.id

        auto_senders[chat_id] = True

        threading.Thread(target=auto_send, args=(chat_id, text, delay)).start()

        bot.reply_to(message,f"✅ Auto message start!\nHar {delay} sec me message jayega.")

    except:
        bot.reply_to(message,"Use:\n/auto seconds message")

# -------- STOP --------
@bot.message_handler(commands=['stop'])
def stop(message):
    chat_id = message.chat.id
    auto_senders[chat_id] = False
    bot.reply_to(message,"🛑 Auto message band kar diya.")

# ===============================
# 🔥 AUTO NICKNAME CHANGE SYSTEM (ADMIN ONLY)
# ===============================
@bot.message_handler(commands=['autoname'])
def auto_name(message):
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ["administrator","creator"]:
            return bot.reply_to(message,"❌ Only Admin can use this command")
    except:
        return

    if len(message.text.split()) < 2:
        return bot.reply_to(message,"Use:\n/autoname NewGroupName")

    new_name = message.text.split(None,1)[1]

    bot.send_message(message.chat.id,"✅ Changing group name...")

    try:
        bot.set_chat_title(message.chat.id, new_name)
        # fast change loop for multiple times (simulate 5/sec)
        for _ in range(5):
            bot.set_chat_title(message.chat.id, new_name)
            time.sleep(0.2)
        bot.send_message(message.chat.id,"✅ Done! Group name changed.")
    except:
        bot.send_message(message.chat.id,"❌ Failed to change group name")

# ===============================
# 🔥 MUSIC PLAYER (ANYONE CAN USE)
# ===============================
@bot.message_handler(commands=['bot'])
def play_song(message):
    if len(message.text.split()) < 2:
        return bot.reply_to(message,"Use:\n/bot song name")

    query = message.text.split(None,1)[1]
    msg = bot.reply_to(message,"🎧 Searching song...")

    try:
        # Download first YouTube result (mp4)
        yt = YouTube(f"https://www.youtube.com/results?search_query={query}")
        stream = yt.streams.filter(only_audio=True).first()
        filename = f"{query}.mp4"
        stream.download(filename=filename)

        # Buttons below song
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📺 Subscribe YouTube", url=YOUTUBE_LINK))
        markup.add(telebot.types.InlineKeyboardButton("🤖 Automatic Message Bot", url=AUTO_MSG_BOT))
        markup.add(telebot.types.InlineKeyboardButton("👨‍💻 Contact Admin Support", url=ADMIN_SUPPORT))
        markup.add(telebot.types.InlineKeyboardButton("🔥 Join Channel", url=CHANNEL_LINK))

        bot.send_audio(message.chat.id, audio=open(filename,'rb'), caption=f"🎵 Playing: {query}", reply_markup=markup)
        msg.delete()
        os.remove(filename)

    except Exception as e:
        msg.edit("❌ Song not found or error occurred")

# ===============================

bot.infinity_polling()
