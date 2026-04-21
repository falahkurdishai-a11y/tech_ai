import os, telebot, requests, time
from telebot import types
from flask import Flask
from threading import Thread

# --- زانیاریێن بۆتی ---
API_TOKEN = "8631109877:AAHFNwNoHJgeSGLUozS2choOiTc17ePqD1Q"
CHANNEL_ID = "@tech_ai_falah"
CHANNEL_URL = "https://t.me/tech_ai_falah"
bot = telebot.TeleBot(API_TOKEN)

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception: return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_sub(user_id):
        bot.send_message(message.chat.id, "سڵاو كاك فەلاح! 🤖\nبۆتێ تە نوژەن بوو بۆ دانلۆدکرنێ.\nتکایە لینکا ڤیدیۆیێ بفرێکه (YouTube, FB, IG, TikTok).")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Channel", url=CHANNEL_URL))
        markup.add(types.InlineKeyboardButton("جوین بووم ✅", callback_data="check"))
        bot.send_message(message.chat.id, f"بەڕێز، بۆ کارپێکرنا بۆتی تکایە سەرەتا جوینی کەناڵێ مە بکه:\n{CHANNEL_URL}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "سوپاس! نوکە دشێی بۆتی بکاربینی ✅")
        bot.edit_message_text("تۆماربوونی تە سەرکەفتوو بوو! لینکا ڤیدیۆیێ بفرێکه.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "تە هێشتا جوین نەکرییه! ❌", show_alert=True)

@bot.message_handler(func=lambda m: True)
def handle_download(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
    
    url = message.text
    if not url.startswith("http"): return
    
    msg = bot.reply_to(message, "⏳ Tech AI خەریکی دانلۆدکردنە...")

    try:
        # بکارئینانا API یەکا ب هێز بۆ هەمی پلاتفۆرمان
        api_url = "https://api.cobalt.tools/api/json"
        payload = {"url": url, "vQuality": "720"}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        if "url" in data:
            video_url = data["url"]
            bot.send_video(message.chat.id, video_url, caption="ڤیدیۆیا تە ئامادەیە ✅\nب ڕێکا: @tech_ai_falah")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("ئیشکال: ئەڤ لینکە ناهێتە دانلۆدکرن یان یا تایبەتە.", message.chat.id, msg.message_id)
            
    except Exception as e:
        bot.edit_message_text("هەڵەیەک ڕوویدا، تکایە دووبارە تاقی بکەوە.", message.chat.id, msg.message_id)

app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def run(): app.run(host='0.0.0.0', port=os.getenv('PORT', 8080))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
