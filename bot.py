import os
import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import yt_dlp
import requests
from urllib.parse import urlparse

# Replace with your bot token from BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHANNEL_USERNAME = "@tech_ai_falah"
CHANNEL_LINK = "https://t.me/tech_ai_falah"

# Check if user has joined the channel (simplified - implement properly with Telegram API if needed)
# For production, you'd use getChatMember API
async def is_user_member(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.first_name
    
    # Keyboard buttons
    keyboard = [
        [InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ I am joined", callback_data='joined')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Welcome {user_name}, you must join our channel first:\n{CHANNEL_LINK}",
        reply_markup=reply_markup
    )

# Callback for "I am joined" button
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # For demo, we're assuming user joined
    # In production, verify membership with getChatMember
    await query.edit_message_text(
        "✅ Success! Send any video link and Tech AI will download it for you.\n\n"
        "Supported platforms:\n"
        "📱 TikTok\n"
        "📸 Instagram\n"
        "📘 Facebook\n"
        "▶️ YouTube"
    )
    context.user_data['verified'] = True

# Function to download video using yt-dlp
async def download_video(url):
    output_template = "downloads/%(title)s_%(id)s.%(ext)s"
    
    ydl_opts = {
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            return file_path, info.get('title', 'video')
    except Exception as e:
        return None, str(e)

# Handle video links
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user verified
    if not context.user_data.get('verified'):
        await start(update, context)
        return
    
    message_text = update.message.text
    user = update.effective_user
    
    # Simple URL validation
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    urls = url_pattern.findall(message_text)
    
    if not urls:
        await update.message.reply_text("❌ Please send a valid video URL.")
        return
    
    video_url = urls[0]
    await update.message.reply_text("⏬ Downloading your video... Please wait.")
    
    # Download video
    file_path, title = await download_video(video_url)
    
    if file_path and os.path.exists(file_path):
        try:
            # Send video to user
            with open(file_path, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file,
                    caption=f"✅ Here's your video from {urlparse(video_url).netloc}\n\n🤖 Powered by Tech AI"
                )
            
            # Clean up - delete file after sending
            os.remove(file_path)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending video: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        await update.message.reply_text(
            f"❌ Failed to download video. Error: {title}\n\n"
            "Possible reasons:\n"
            "- Private video\n"
            "- Unsupported platform\n"
            "- Video removed\n\n"
            "Try another link."
        )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred. Please try again later.")

# Main function
def main():
    # Create downloads folder if not exists
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
