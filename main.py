import telebot
import requests
from telebot import types

# توکنێ بوت فازەری ل ڤێرە دانە
TOKEN = '8631109877:AAHFNwNoHJgeSGLUozS2choOiTc17ePqD1Q'
# ناڤێ چەناڵێ تە
CHANNEL_USERNAME = 'tech_ai_falah'

bot = telebot.TeleBot(TOKEN)

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
        bot.send_message(message.chat.id, f"خێرهاتی بەڕێز {name} ✅\nلینکی فڕێکە دا بۆتە دانلوت بکەم (TikTok, Insta, FB, YT)")
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Join Channel 📢", url=f"https://t.me/{CHANNEL_USERNAME}")
        btn2 = types.InlineKeyboardButton("I am joined ✅", callback_data="check")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, f"خێرهاتى بەڕێز {name}، پێدڤييه‌ ده‌ستپێكێ چه‌نالێ مه‌ جوين بكهى:\n@{CHANNEL_USERNAME}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.edit_message_text("سوپاس بۆ جوینکرن! نوکە لینکی فڕێکە.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "تە هێشتا جوین نەکرییە! ⚠️", show_alert=True)

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def download_process(message):
    if not check_sub(message.from_user.id):
        start(message)
        return

    url = message.text
    msg = bot.reply_to(message, "کێمەک چاڤەڕێ بە... پەیجێ **Tech AI** یێ ڤیدیۆیێ ئامادە دکەت ⏳")

    try:
        # بکارئینانا سێرڤەرێ Cobalt بۆ دانلوتێ
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "vQuality": "720",
            "isAudioOnly": False
        }

        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        if "url" in data:
            bot.send_video(message.chat.id, data["url"], caption="ڤیدیۆیا تە ب سەرکەفتی هاتە دانلوتکرن ✅\nBy: @tech_ai_falah")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("ببورە، کێشەک هەبوو! دیتبیت ڤیدیۆیا تە تایبەتە (Private) یان لینک یێ خەلەتە.", message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"ئێشکاڵەک هەبوو د سێرڤەری دا، هیڤییە پاشتر هەوڵ بدە ڤە.", message.chat.id, msg.message_id)

bot.polling()
