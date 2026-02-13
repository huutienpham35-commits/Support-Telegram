import os
import logging
import json
from datetime import datetime
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token từ biến môi trường
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_IDS = [123456789, 987654321]  # Thay bằng ID Telegram của bạn

# File lưu dữ liệu
DATA_FILE = 'bot_data.json'

class BotDatabase:
    """Quản lý dữ liệu bot"""
    
    def __init__(self):
        self.data = self.load_data()
    
    def load_data(self):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {
                'users': {},
                'total_queries': 0,
                'commands_used': {},
                'messages': []
            }
    
    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_user(self, user_id, username, first_name):
        user_id = str(user_id)
        if user_id not in self.data['users']:
            self.data['users'][user_id] = {
                'username': username,
                'first_name': first_name,
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'commands_count': 0
            }
        else:
            self.data['users'][user_id]['last_seen'] = datetime.now().isoformat()
        self.save_data()
    
    def log_command(self, user_id, command):
        user_id = str(user_id)
        self.data['total_queries'] += 1
        
        # Đếm lệnh
        if command not in self.data['commands_used']:
            self.data['commands_used'][command] = 0
        self.data['commands_used'][command] += 1
        
        # Cập nhật user
        if user_id in self.data['users']:
            self.data['users'][user_id]['commands_count'] += 1
        
        self.save_data()
    
    def add_message(self, user_id, message):
        self.data['messages'].append({
            'user_id': str(user_id),
            'message': message,
            'time': datetime.now().isoformat()
        })
        self.save_data()

# Khởi tạo database
db = BotDatabase()

# ============= CÁC HÀM KIỂM TRA ADMIN =============
def is_admin(user_id):
    return user_id in ADMIN_IDS

# ============= LỆNH CHO NGƯỜI DÙNG =============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    db.log_command(user.id, '/start')
    
    welcome_text = f"""
👋 Chào {user.first_name}! Chào mừng bạn đến với bot của HuuTien Store!

Các lệnh có sẵn:
/website - Truy cập website
/help - Xem hướng dẫn
/about - Giới thiệu

📢 Admin: {is_admin(user.id)}
    """
    
    await update.message.reply_text(welcome_text)

async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.log_command(user.id, '/website')
    
    keyboard = [
        [InlineKeyboardButton("🌐 Truy cập Website", url='https://huutien.store/')],
        [InlineKeyboardButton("📞 Liên hệ", url='https://t.me/huutien_store')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '🏠 *HuuTien Store*\n\n'
        'Nhấn nút bên dưới để truy cập website:',
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.log_command(user.id, '/help')
    
    help_text = """
📚 *Hướng dẫn sử dụng bot*

Các lệnh cơ bản:
• /start - Khởi động bot
• /website - Xem website
• /about - Thông tin bot

Cần hỗ trợ? Liên hệ @huutien_store
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.log_command(user.id, '/about')
    
    about_text = """
🤖 *Về bot này*

• Tên: HuuTien Store Bot
• Phiên bản: 1.0.0
• Chức năng: Hỗ trợ khách hàng
• Website: huutien.store

👨‍💻 Developer: @huutien_dev
    """
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

# ============= ADMIN DASHBOARD =============
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dashboard chính cho Admin"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Bạn không có quyền truy cập!")
        return
    
    db.log_command(user.id, '/admin')
    
    # Thống kê nhanh
    total_users = len(db.data['users'])
    total_queries = db.data['total_queries']
    
    # Tạo menu Admin
    keyboard = [
        [InlineKeyboardButton("👥 Quản lý Users", callback_data='admin_users')],
        [InlineKeyboardButton("📊 Thống kê", callback_data='admin_stats')],
        [InlineKeyboardButton("📝 Lịch sử lệnh", callback_data='admin_commands')],
        [InlineKeyboardButton("📨 Tin nhắn gần đây", callback_data='admin_messages')],
        [InlineKeyboardButton("⚙️ Cài đặt", callback_data='admin_settings')],
        [InlineKeyboardButton("🔙 Thoát", callback_data='admin_exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
👑 *ADMIN DASHBOARD*
━━━━━━━━━━━━━━━━━━━━━
📊 *Tổng quan:*
• Users: {total_users}
• Lượt dùng: {total_queries}
• Admin ID: {user.id}

📌 Chọn chức năng:
    """
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý các nút bấm trong Admin Panel"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    if not is_admin(user.id):
        await query.edit_message_text("⛔ Bạn không có quyền truy cập!")
        return
    
    data = query.data
    
    if data == 'admin_users':
        # Danh sách users
        users = db.data['users']
        text = "👥 *Danh sách Users:*\n\n"
        
        for uid, info in list(users.items())[:10]:  # Chỉ hiện 10 user gần nhất
            text += f"• ID: `{uid}`\n"
            text += f"  Name: {info['first_name']}\n"
            text += f"  Username: @{info['username'] if info['username'] else 'N/A'}\n"
            text += f"  Commands: {info['commands_count']}\n"
            text += f"  Last seen: {info['last_seen'][:10]}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data='admin_back')]]
        await query.edit_message_text(text, parse_mode='Markdown', 
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'admin_stats':
        # Thống kê chi tiết
        text = "📊 *THỐNG KÊ CHI TIẾT*\n\n"
        text += f"• Tổng users: {len(db.data['users'])}\n"
        text += f"• Tổng lượt dùng: {db.data['total_queries']}\n"
        text += f"• Tổng lệnh: {len(db.data['commands_used'])}\n"
        text += f"• Tin nhắn: {len(db.data['messages'])}\n\n"
        
        # Top lệnh dùng nhiều
        text += "*Top lệnh phổ biến:*\n"
        sorted_commands = sorted(db.data['commands_used'].items(), 
                               key=lambda x: x[1], reverse=True)[:5]
        for cmd, count in sorted_commands:
            text += f"  {cmd}: {count} lượt\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data='admin_back')]]
        await query.edit_message_text(text, parse_mode='Markdown',
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'admin_commands':
        text = "📝 *LỊCH SỬ LỆNH*\n\n"
        for cmd, count in db.data['commands_used'].items():
            text += f"• {cmd}: {count} lượt\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data='admin_back')]]
        await query.edit_message_text(text, parse_mode='Markdown',
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'admin_messages':
        text = "📨 *TIN NHẮN GẦN ĐÂY*\n\n"
        for msg in db.data['messages'][-5:]:  # 5 tin nhắn gần nhất
            text += f"• User {msg['user_id']}: {msg['message'][:50]}\n"
            text += f"  {msg['time'][:16]}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data='admin_back')]]
        await query.edit_message_text(text, parse_mode='Markdown',
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'admin_settings':
        text = "⚙️ *CÀI ĐẶT*\n\n"
        text += "• Tự động lưu dữ liệu: ✅\n"
        text += f"• Admin IDs: {ADMIN_IDS}\n"
        text += "• Mode: Production\n"
        
        keyboard = [
            [InlineKeyboardButton("📤 Export Data", callback_data='admin_export')],
            [InlineKeyboardButton("🔄 Reset Stats", callback_data='admin_reset')],
            [InlineKeyboardButton("🔙 Quay lại", callback_data='admin_back')]
        ]
        await query.edit_message_text(text, parse_mode='Markdown',
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'admin_export':
        # Export dữ liệu ra file
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(db.data, f, indent=2)
        
        await query.edit_message_text(f"✅ Đã export data thành công!\nFile: {filename}")
    
    elif data == 'admin_reset':
        # Reset thống kê
        db.data['total_queries'] = 0
        db.data['commands_used'] = {}
        db.save_data()
        await query.edit_message_text("✅ Đã reset thống kê!")
    
    elif data == 'admin_back':
        # Quay lại menu chính
        keyboard = [
            [InlineKeyboardButton("👥 Quản lý Users", callback_data='admin_users')],
            [InlineKeyboardButton("📊 Thống kê", callback_data='admin_stats')],
            [InlineKeyboardButton("📝 Lịch sử lệnh", callback_data='admin_commands')],
            [InlineKeyboardButton("📨 Tin nhắn gần đây", callback_data='admin_messages')],
            [InlineKeyboardButton("⚙️ Cài đặt", callback_data='admin_settings')]
        ]
        await query.edit_message_text("👑 *ADMIN DASHBOARD*\n\nChọn chức năng:",
                                    parse_mode='Markdown',
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'admin_exit':
        await query.edit_message_text("👋 Đã thoát Admin Panel!")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gửi tin nhắn hàng loạt (admin only)"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Bạn không có quyền!")
        return
    
    # Lấy nội dung tin nhắn
    message = ' '.join(context.args)
    if not message:
        await update.message.reply_text("Cách dùng: /broadcast [nội dung]")
        return
    
    # Gửi cho tất cả users
    sent = 0
    for uid in db.data['users'].keys():
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 *THÔNG BÁO:*\n\n{message}", parse_mode='Markdown')
            sent += 1
        except:
            pass
    
    await update.message.reply_text(f"✅ Đã gửi thông báo đến {sent} users!")

# ============= XỬ LÝ TIN NHẮN =============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn thường"""
    user = update.effective_user
    message_text = update.message.text
    
    # Lưu tin nhắn
    db.add_message(user.id, message_text[:100])
    
    # Phản hồi tự động
    if 'hello' in message_text.lower() or 'hi' in message_text.lower():
        await update.message.reply_text(f"Xin chào {user.first_name}! Bạn cần giúp gì không?")
    else:
        await update.message.reply_text("Cảm ơn bạn đã gửi tin nhắn! Admin sẽ phản hồi sớm.")

# ============= MAIN FUNCTION =============
def main():
    """Khởi chạy bot"""
    print("🚀 Bot is starting...")
    print(f"👑 Admin IDs: {ADMIN_IDS}")
    
    # Tạo application
    application = Application.builder().token(TOKEN).build()
    
    # Thêm handlers cho user
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('website', website))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('about', about))
    
    # Thêm handlers cho admin
    application.add_handler(CommandHandler('admin', admin_panel))
    application.add_handler(CommandHandler('broadcast', broadcast))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern='^admin_'))
    
    # Handler cho tin nhắn thường
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Chạy bot
    print("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
