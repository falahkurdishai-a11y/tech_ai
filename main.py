import telebot
from telebot import types
import requests

# توکنێ تە یێ بوت فازەری
TOKEN = '8631109877:AAHFNwNoHJgeSGLUozS2choOiTc17ePqD1Q'
# ناڤێ چەناڵێ تە بێ @
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
    user_id = message.from_user.id
    
    if check_sub(user_id):
        bot.send_message(user_id, f"تو سه‌ركه‌فتى به‌ڕێز {name}، هه‌ر ڤيديۆيه‌كا ته‌ بڤێت لينكى فڕێكه‌، په‌يچێ **Tech AI** دێ بۆته‌ دانلوت كه‌ت.")
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Channel 📢", url=f"https://t.me/{CHANNEL_USERNAME}")
        btn2 = types.InlineKeyboardButton("I am joined ✅", callback_data="check")
        markup.add(btn1)
        markup.add(btn2)
        
        bot.send_message(user_id, f"خێرهاتى به‌ڕێز {name}، پێدڤييه‌ ده‌ستپێكێ چه‌نالێ مه‌ جوين بكهى:\nhttps://t.me/{CHANNEL_USERNAME}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.edit_message_text("تو سه‌ركه‌فتى! نوکە لینکی فڕێکە پەیجێ Tech AI دێ بۆتە دانلوت کەت.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "تە هێشتا جوین نەکرییە! ⚠️", show_alert=True)

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def download_video(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        start(message)
        return

    url = message.text
    bot.reply_to(message, "کێمەک چاڤەڕێ بە... پەیجێ **Tech AI** یێ ڤیدیۆیێ ئامادە دکەت ⏳")

    try:
        # بکارئینانا API بۆ دانلوتکرنا ڤیدیۆیان
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        data = {
            "url": url,
            "vQuality": "720"
        }
        
        response = requests.post(api_url, json=data, headers=headers)
        res_data = response.json()

        if "url" in res_data:
            video_link = res_data["url"]
            bot.send_video(message.chat.id, video_link, caption="ڤیدیۆیا تە ب سەرکەفتی هاتە دانلوتکرن ب رێکا Tech AI ✅")
        else:
            bot.reply_to(message, "ببورە، من نەشیا ڤێ ڤیدیۆیێ دانلوت بکەم. پشت راست بە کو لینکێ تە یێ دروستە.")
            
    except Exception as e:
        bot.reply_to(message, "ئێشکاڵەک د سێرڤەری دا چێبوو، هیڤییە پاشتر هەول بدەڤە.")

bot.polling()
