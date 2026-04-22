import telebot
import requests
import re
from telebot import types

# زانیاریێن بوتێ تە
TOKEN = '8631109877:AAHFNwNoHJgeSGLUozS2choOiTc17ePqD1Q'
CHANNEL_USERNAME = 'tech_ai_falah'

bot = telebot.TeleBot(TOKEN)

# فەنکشنا پشکنینا ئەندامبوونی
def check_sub(user_id):
    try:
        status = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, f"خێرهاتی پاشا {name} بۆ Tech AI ✅\nلینکی فڕێکە (TikTok, FB, Insta, YT)")
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Join Channel 📢", url=f"https://t.me/{CHANNEL_USERNAME}")
        btn2 = types.InlineKeyboardButton("I am joined ✅", callback_data="check")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, f"سلاڤ بەڕێز {name}، بۆ کارکرنا بوتێ پێدڤییە جوینی چەناڵی ببی:\n@{CHANNEL_USERNAME}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.edit_message_text("سوپاس! نوکە لینکی فڕێکە.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "تە هێشتا جوین نەکرییە! ⚠️", show_alert=True)

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def download_engine(message):
    if not check_sub(message.from_user.id):
        start(message)
        return

    url = message.text
    msg = bot.reply_to(message, "کێمەک چاڤەڕێ بە... پەیجێ **Tech AI** یێ ڤیدیۆیێ ئامادە دکەت ⏳")

    # بکارئینانا APIیا جیهانی یا Cobalt (ئەڤە باشترینە بۆ هەمی بەرنامان)
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    # رێکخستنا کوالێتیا ڤیدیۆیێ
    payload = {
        "url": url,
        "vQuality": "720",
        "isAudioOnly": False,
        "filenamePattern": "basic"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        if "url" in data:
            bot.send_video(message.chat.id, data["url"], caption="ڤیدیۆیا تە ئامادەیە ب رێکا Tech AI ✅\nBy: @tech_ai_falah")
            bot.delete_message(message.chat.id, msg.message_id)
        elif "picker" in data:
            # ئەڤە بۆ حالەتێن تیکتۆکێ یێن کو چەند وێنەک د ناڤ دانە (Slide)
            bot.send_message(message.chat.id, "ئەڤ لینکە چەند وێنەک تێدانە، بوت بتنێ ڤیدیۆیان دانلوت دکەت.")
        else:
            bot.edit_message_text("ببورە! سێرڤەر نەشیام ڤیدیۆیێ دانلوت بکەت. پشت راست ببە کو ڤیدیۆیا تە گشتییە (Public).", message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text("ئێشکاڵەک هەبوو، یان سێرڤەر یێ مژیولە. هیڤییە دووبارە تاقی بکە ڤە.", message.chat.id, msg.message_id)

bot.polling()
