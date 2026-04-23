import os
import re
import asyncio
import shutil
from pathlib import Path
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration - Get from environment variables
BOT_TOKEN = os.getenv(8753483850:AAG9Is_8vdY__Tf4V441Rbs_SJ-StNyln2w)
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "tech_ai_falah")
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

# Temporary download folder (Northflank has /tmp writable)
DOWNLOAD_FOLDER = Path("/tmp/downloads")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Supported platforms
PLATFORM_PATTERNS = {
    "youtube": r"(youtube\.com|youtu\.be)",
    "tiktok": r"(tiktok\.com)",
    "instagram": r"(instagram\.com|instagr\.am)",
    "facebook": r"(facebook\.com|fb\.watch|fb\.com)"
}

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user has joined the required channel"""
    try:
        user_id = update.effective_user.id
        chat_member = await context.bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME}", 
            user_id=user_id
        )
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Membership check error: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ I am joined", callback_data="check_joined")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Welcome {user.first_name}, you must join our channel first: {CHANNEL_LINK}",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_joined":
        is_member = await check_membership(update, context)
        
        if is_member:
            await query.edit_message_text(
                "✅ Success! Send any video link and Tech AI will download it for you"
            )
        else:
            keyboard = [
                [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ I am joined", callback_data="check_joined")]
            ]
            await query.edit_message_text(
                f"❌ You haven't joined our channel yet. Please join first: {CHANNEL_LINK}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

def get_video_info(url: str):
    """Extract video info without downloading"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            logger.error(f"Info extraction error: {e}")
            return None

async def download_video(url: str) -> Optional[Path]:
    """Download video using yt-dlp and return file path"""
    # First check video size without downloading
    info = await asyncio.to_thread(get_video_info, url)
    
    if not info:
        return None
    
    # Get estimated filesize
    filesize = None
    if 'filesize' in info and info['filesize']:
        filesize = info['filesize']
    elif 'filesize_approx' in info and info['filesize_approx']:
        filesize = info['filesize_approx']
    
    # Telegram limit is 50MB
    if filesize and filesize > 50 * 1024 * 1024:
        logger.warning(f"Video too large: {filesize} bytes")
        return None
    
    ydl_opts = {
        'outtmpl': str(DOWNLOAD_FOLDER / '%(title)s_%(id)s.%(ext)s'),
        'format': 'best[height<=720][filesize<50M]/best[height<=480][filesize<50M]/best[filesize<50M]',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        # Remove cookies.txt if you don't have it
        # 'cookiefile': 'cookies.txt',
    }
    
    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            
            if info and 'requested_downloads' in info and info['requested_downloads']:
                file_path = Path(info['requested_downloads'][0]['filepath'])
                return file_path
            elif info and 'entries' in info and info['entries']:
                # Handle playlists - take first video
                first_entry = info['entries'][0]
                if first_entry and 'requested_downloads' in first_entry:
                    file_path = Path(first_entry['requested_downloads'][0]['filepath'])
                    return file_path
    except Exception as e:
        logger.error(f"Download error: {e}")
        return None
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages containing video links"""
    user = update.effective_user
    message_text = update.message.text.strip()
    
    # Check membership first
    if not await check_membership(update, context):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ I am joined", callback_data="check_joined")]
        ]
        await update.message.reply_text(
            f"❌ You need to join our channel first: {CHANNEL_LINK}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Check if URL is from supported platform
    supported = False
    supported_platforms = []
    for platform, pattern in PLATFORM_PATTERNS.items():
        if re.search(pattern, message_text, re.IGNORECASE):
            supported = True
            supported_platforms.append(platform)
    
    if not supported:
        await update.message.reply_text(
            "❌ Unsupported platform.\n\n"
            "Please send links from:\n"
            "• YouTube\n"
            "• TikTok\n"
            "• Instagram\n"
            "• Facebook\n\n"
            "Make sure the link is public and accessible."
        )
        return
    
    # Send "processing" message
    processing_msg = await update.message.reply_text(
        f"⏬ Downloading video from {', '.join(supported_platforms)}...\n"
        f"This may take a few moments."
    )
    
    file_path = None
    try:
        # Download video
        file_path = await download_video(message_text)
        
        if not file_path or not file_path.exists():
            await processing_msg.edit_text(
                "❌ Failed to download video.\n\n"
                "Possible reasons:\n"
                "• Video is private or deleted\n"
                "• Video exceeds 50MB (Telegram limit)\n"
                "• Unsupported video format\n"
                "• Platform requires login (try public videos)"
            )
            return
        
        # Check file size again
        file_size = file_path.stat().st_size
        if file_size > 50 * 1024 * 1024:
            await processing_msg.edit_text(
                f"❌ Video size is {file_size / (1024*1024):.1f}MB, which exceeds Telegram's 50MB limit."
            )
            file_path.unlink()
            return
        
        # Send video to user with progress indication
        await processing_msg.edit_text("📤 Uploading video to Telegram...")
        
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="✅ **Here's your video!**\n\n"
                       f"📥 Downloaded by @{CHANNEL_USERNAME}\n"
                       f"📏 Size: {file_size / (1024*1024):.1f}MB",
                parse_mode='Markdown'
            )
        
        # Clean up
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await processing_msg.edit_text(
            "❌ An unexpected error occurred.\n"
            "Please try again with a different link or contact support."
        )
    finally:
        # Clean up any leftover files
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except:
                pass

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred. Please try again later."
        )

async def post_init(application: Application):
    """Called after bot initialization"""
    logger.info(f"Bot started! Username: @{(await application.bot.get_me()).username}")

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")
    
    print(f"Starting bot with channel: @{CHANNEL_USERNAME}")
    print(f"Download folder: {DOWNLOAD_FOLDER}")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
