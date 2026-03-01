from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
import sqlite3

# ================== CẤU HÌNH ==================
TOKEN = "8691746572:AAHRWWruEtJjZBWgpX359JsW4x7ivDN9Bgw"
PHOTO_START = "https://i.postimg.cc/L6cvFG1N/photo-2025-02-22-19-57-44.jpg"
PHOTO_SUCCESS = "https://sf-static.upanhlaylink.com/img/image_202603019bd99f8ef5d51f14a5b165f595f9a287.jpg"
CHANNEL_1 = "@huongdan03"
CHANNEL_2 = "@huongdan05"

ADMIN_IDS = [6165606674, 1682351727, 7312813026]  # 🔴 THAY ID TELEGRAM CỦA BẠN
USERS_FILE = "users.txt"

# ================== DATABASE REF ==================
conn = sqlite3.connect("ref_data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ref_users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    ref_by INTEGER,
    ref_count INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS withdraw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    status TEXT
)
""")

conn.commit()

# ================== LOAD USER ==================
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return set(int(line.strip()) for line in f)
    except:
        return set()

def save_user(user_id):
    with open(USERS_FILE, "a") as f:
        f.write(str(user_id) + "\n")

users = load_users()

# ================== BÀN PHÍM GAME ==================
game_keyboard = ReplyKeyboardMarkup(
    [
        ["🧧 QQLive 97K", "🧧 MMLive 88K"],
        ["🧧 BenBet 58K", "🧧 Winer 100K"],
        ["👥 Mời Bạn Bè","💸 Rút Tiền"],
        ["📊 Thống Kê"  , "💳 Số Dư"],
        ["💰 Kiếm Tiền"]
    ],
    resize_keyboard=True
)

# ================== CHECK JOIN ==================
async def check_user(bot, user_id):
    try:
        member1 = await bot.get_chat_member(CHANNEL_1, user_id)
        member2 = await bot.get_chat_member(CHANNEL_2, user_id)

        if member1.status in ["member", "administrator", "creator"] and \
           member2.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False
    except:
        return False

# ================== START + REF ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    args = context.args

    # Lưu user
    if user not in users:
        users.add(user)
        save_user(user)

    # Kiểm tra user đã tồn tại trong DB chưa
    cursor.execute("SELECT * FROM ref_users WHERE user_id=?", (user,))
    data = cursor.fetchone()

    if not data:
        ref_by = None

        # Nếu có ref
        if args:
            try:
                ref_id = int(args[0])
                if ref_id != user:
                    cursor.execute("SELECT * FROM ref_users WHERE user_id=?", (ref_id,))
                    if cursor.fetchone():
                        ref_by = ref_id
                        cursor.execute(
                            "UPDATE ref_users SET balance = balance + 5000, ref_count = ref_count + 1 WHERE user_id=?",
                            (ref_id,)
                        )
            except:
                pass

        cursor.execute(
            "INSERT INTO ref_users (user_id, ref_by) VALUES (?,?)",
            (user, ref_by)
        )
        conn.commit()

    # Kiểm tra join kênh
    joined = await check_user(context.bot, user)

    if joined:
        await update.message.reply_photo(
            photo=PHOTO_SUCCESS,
            caption="✅ Bạn đã tham gia đầy đủ!\n\nChọn game bên dưới:",
            reply_markup=game_keyboard
        )
        return

    keyboard = [
        [
            InlineKeyboardButton("Kênh 1", url="https://t.me/huongdan03"),
            InlineKeyboardButton("Kênh 2", url="https://t.me/huongdan05")
        ],
        [InlineKeyboardButton("✅ Tôi đã tham gia - Xác minh", callback_data="check")]
    ]

    await update.message.reply_photo(
        photo=PHOTO_START,
        caption="🎁 Vui lòng tham gia các kênh để xác nhận.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== NÚT XÁC MINH ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user.id
    await query.answer()

    joined = await check_user(context.bot, user)

    if joined:
        await query.message.delete()

        await context.bot.send_photo(
            chat_id=user,
            photo=PHOTO_SUCCESS,
            caption="✅ Xác nhận thành công!\n\nChọn game bên dưới:",
            reply_markup=game_keyboard
        )
    else:
        await query.answer("⚠️ Bạn chưa tham gia đủ kênh!", show_alert=True)

# ================== XỬ LÝ MENU ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user.id

    if text == "🧧 QQLive 97K":
        await context.bot.forward_message(update.effective_chat.id, "@huongdan05", 57)

    elif text == "🧧 MMLive 88K":
        await context.bot.forward_message(update.effective_chat.id, "@huongdan05", 58)

    elif text == "🧧 BenBet 58K":
        await context.bot.forward_message(update.effective_chat.id, "@huongdan05", 54)

    elif text == "🧧 Winer 100K":
        await context.bot.forward_message(update.effective_chat.id, "@huongdan05", 51)

    elif text == "💰 Kiếm Tiền":
        await update.message.reply_photo(
            photo="https://sf-static.upanhlaylink.com/img/image_20260225b544cf6f824a0c748f95a12684178310.jpg",
            caption="👉🏻 thu acc tele 20k-50k/1 acc ai bán ib @polyme2"
        )

    elif text == "👥 Mời Bạn Bè":
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={user}"

        await update.message.reply_text(
            f"👥 Link mời của bạn:\n\n{link}\n\nMỗi người tham gia bạn nhận 5.000đ 💰"
        )

    elif text == "💳 Số Dư":
        cursor.execute("SELECT balance FROM ref_users WHERE user_id=?", (user,))
        row = cursor.fetchone()
        balance = row[0] if row else 0
        await update.message.reply_text(f"💰 Số dư của bạn: {balance:,} đ")

    elif text == "📊 Thống Kê":
        cursor.execute("SELECT ref_count FROM ref_users WHERE user_id=?", (user,))
        row = cursor.fetchone()
        count = row[0] if row else 0
        await update.message.reply_text(f"👥 Bạn đã mời: {count} người")

    elif text == "💸 Rút Tiền":
        cursor.execute("SELECT balance FROM ref_users WHERE user_id=?", (user,))
        row = cursor.fetchone()
        balance = row[0] if row else 0

        if balance < 50000:
            await update.message.reply_text("❌ Cần tối thiểu 50.000đ để rút.")
        else:
            cursor.execute(
                "INSERT INTO withdraw (user_id, amount, status) VALUES (?,?,?)",
                (user, balance, "pending")
            )
            conn.commit()

            for admin in ADMIN_IDS:
                await context.bot.send_message(
                    admin,
                    f"💸 Yêu cầu rút tiền\nUser: {user}\nSố tiền: {balance:,} đ"
                )

            await update.message.reply_text("✅ Đã gửi yêu cầu rút tiền. Chờ admin duyệt.")

# ================== BROADCAST ==================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Bạn không có quyền.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /broadcast <message_id>")
        return

    message_id = int(context.args[0])
    success = 0

    for user_id in users:
        try:
            await context.bot.forward_message(
                chat_id=user_id,
                from_chat_id="@huongdan05",
                message_id=message_id
            )
            success += 1
        except:
            pass

    await update.message.reply_text(f"✅ Đã gửi cho {success} người.")

# ================== RUN BOT ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot đang chạy...")
app.run_polling()