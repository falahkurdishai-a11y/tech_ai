import telebot
import requests
import time
from telebot import types

# 1. ل ڤێرە توکنێ بوت فازەری دانە
TOKEN = '8631109877:AAHFNwNoHJgeSGLUozS2choOiTc17ePqD1Q'
# 2. ناڤێ چەناڵێ تە بێ @
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
        bot.send_message(message.chat.id, f"خێرهاتی کاکە {name} بۆ بوتێ **Tech AI** ✅\n\nلینکی ڤیدیۆیێ فڕێکە دا ب بێ کێشە بۆتە دانلوت بکەم (TikTok, Insta, FB, YT).")
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Join Channel 📢", url=f"https://t.me/{CHANNEL_USERNAME}")
        btn2 = types.InlineKeyboardButton("I am joined ✅", callback_data="check")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, f"سلاڤ بەڕێز {name}، پێدڤييه‌ ده‌ستپێكێ جوينى چه‌نالێ مه‌ ببی:\n@{CHANNEL_USERNAME}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.edit_message_text("سوپاس! نوکە هەر لینکەکێ بڤێت فڕێکە.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "تە هێشتا جوین نەکرییە! ⚠️", show_alert=True)

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def download_logic(message):
    if not check_sub(message.from_user.id):
        start(message)
        return

    url = message.text
    status_msg = bot.reply_to(message, "کێمەک چاڤەڕێ بە... پەیجێ **Tech AI** یێ ڤیدیۆیێ ئامادە دکەت ⏳")

    # بکارئینانا سێرڤەرێ Universal Downloader (ئەڤە هەمی سایتان ساپۆرت دکەت)
    api_url = "https://social-download-all-in-one.p.rapidapi.com/v1/social/autodetect"
    
    # تێبینی: ئەگەر ئەڤ API کار نەکر، دێ Cobalt API یا بەری نوکە بکار هێین بەلێ ب سێرڤەرەکێ جودا
    payload = {"url": url}
    headers = {
        "x-rapidapi-key": "ل ڤێرە کلیلەکا RapidAPI پێدڤییە یان بکارئینانا Cobalt",
        "x-rapidapi-host": "social-download-all-in-one.p.rapidapi.com"
    }

    try:
        # ئەڤە ڕێکا کۆباڵتە (چاکی هێزترە بۆ تیکتۆک و ئینستا)
        cobalt_res = requests.post("https://api.cobalt.tools/api/json", 
                                 json={"url": url, "vQuality": "720"},
                                 headers={"Accept": "application/json", "Content-Type": "application/json"})
        
        data = cobalt_res.json()

        if "url" in data:
            bot.send_video(message.chat.id, data["url"], caption="ڤیدیۆیا تە ب سەرکەفتی هاتە دانلوتکرن ✅\nBy: @tech_ai_falah")
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("ببورە، ئەڤ لینکە ل دەڤ من کار ناکەت. هیڤییە لینکەکێ دروست بنێرە.", message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text("ئێشکاڵەک هەبوو، یان سێرڤەر یێ مژیولە. دووبارە هەول بدە ڤە.", message.chat.id, status_msg.message_id)

bot.polling()
