import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Lấy token từ biến môi trường
TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Chào bạn! Tôi là bot hỗ trợ.\n'
        'Sử dụng /website để truy cập website.'
    )

async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 Truy cập Website", url='https://huutien.store/')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '🏠 *HuuTien Store*\n\n'
        'Nhấn nút bên dưới để truy cập website:',
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

def main():
    """Khởi chạy bot"""
    print("🚀 Bot is starting...")
    
    # Tạo application
    application = Application.builder().token(TOKEN).build()
    
    # Thêm handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('website', website))
    
    # Chạy bot (blocking)
    print("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
