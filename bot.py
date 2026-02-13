from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = 'YOUR_BOT_TOKEN_HERE'

async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị website với nút bấm"""
    
    # Tạo nút bấm
    keyboard = [
        [InlineKeyboardButton("🌐 Truy cập Website", url='https://huutien.store/')],
        [InlineKeyboardButton("📞 Liên hệ", url='https://t.me/your_contact')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Gửi tin nhắn với nút bấm
    await update.message.reply_text(
        '🏠 *Website HuuTien Store*\n\n'
        'Chào mừng bạn đến với website của chúng tôi!\n'
        'Nhấn nút bên dưới để truy cập.',
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# ... phần còn lại tương tự
