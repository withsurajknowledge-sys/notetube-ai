import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Temporary in-memory credits
# Later we will replace this with a proper database.
users = {}


def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "free_credits": 2,
            "paid_credits": 0,
        }
    return users[user_id]


def is_youtube_url(text):
    pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/\S+"
    return re.search(pattern, text) is not None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    keyboard = [
        [InlineKeyboardButton("🎬 Create PDF Notes", callback_data="create")],
        [InlineKeyboardButton("📊 My Credits", callback_data="credits")],
        [InlineKeyboardButton("💳 Buy Plan", callback_data="buy")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ]

    text = (
        "📚 *AI YouTube Notes Bot*\n\n"
        "🎁 *Your FREE DEMO has started!*\n\n"
        "You get:\n"
        "✅ 2 FREE YouTube → PDF Notes\n"
        "✅ AI-generated notes\n"
        "✅ Important points\n"
        "✅ Formulas & definitions\n"
        "✅ Clean & professional PDF\n\n"
        f"📊 *Free Credits: {user['free_credits']}/2*\n\n"
        "👇 Send a YouTube video link to get started."
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    await update.message.reply_text(
        f"📊 *Your Credits*\n\n"
        f"🎁 Free Credits: {user['free_credits']}\n"
        f"⭐ Paid Credits: {user['paid_credits']}\n\n"
        "Send a YouTube link to create your notes.",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *How to use AI YouTube Notes Bot*\n\n"
        "1️⃣ Send a YouTube video link.\n"
        "2️⃣ The bot will process the video.\n"
        "3️⃣ Your PDF notes will be generated.\n"
        "4️⃣ Download the PDF directly from Telegram.\n\n"
        "🎁 New users get 2 FREE PDF Notes.",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = get_user(update.effective_user.id)

    if not is_youtube_url(text):
        await update.message.reply_text(
            "❌ Please send a valid YouTube video link.\n\n"
            "Example:\n"
            "https://youtube.com/watch?v=example"
        )
        return

    if user["free_credits"] <= 0 and user["paid_credits"] <= 0:
        keyboard = [
            [InlineKeyboardButton("💳 Get ₹49 Starter Plan", callback_data="buy")],
            [InlineKeyboardButton("📊 My Credits", callback_data="credits")],
        ]

        await update.message.reply_text(
            "⭐ *Your FREE DEMO is completed!*\n\n"
            "You have used both free PDF credits.\n\n"
            "Continue creating AI PDF Notes with our Starter Plan.\n\n"
            "💳 *₹49 STARTER PLAN*\n"
            "✅ 20 PDF Notes\n"
            "✅ AI-generated study notes\n"
            "✅ Important concepts & formulas\n"
            "✅ Professional PDF format\n"
            "✅ 30 days validity",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    processing = await update.message.reply_text(
        "🔗 YouTube Link Received ✅\n\n"
        "⏳ *Processing your video...*\n\n"
        "📝 Extracting transcript...\n"
        "🤖 Generating AI notes...\n"
        "📄 Creating PDF...",
        parse_mode="Markdown",
    )

    # Demo response for now.
    # YouTube transcript + AI + PDF generation will be added next.
    await processing.edit_text(
        "🎉 *Demo processing completed!*\n\n"
        "The YouTube → AI → PDF engine will be connected in the next step.\n\n"
        "📊 Your current credits are being tracked.",
        parse_mode="Markdown",
    )

    if user["free_credits"] > 0:
        user["free_credits"] -= 1
    else:
        user["paid_credits"] -= 1

    await update.message.reply_text(
        f"📊 Free Credits Remaining: {user['free_credits']}/2"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = get_user(query.from_user.id)

    if query.data == "credits":
        await query.message.reply_text(
            f"📊 *Your Credits*\n\n"
            f"🎁 Free Credits: {user['free_credits']}\n"
            f"⭐ Paid Credits: {user['paid_credits']}",
            parse_mode="Markdown",
        )

    elif query.data == "create":
        await query.message.reply_text(
            "🎬 Send me a YouTube video link."
        )

    elif query.data == "help":
        await query.message.reply_text(
            "❓ Send a YouTube video link and I'll create PDF study notes for you."
        )

    elif query.data == "buy":
        await query.message.reply_text(
            "💳 *₹49 STARTER PLAN*\n\n"
            "✅ 20 PDF Notes\n"
            "✅ AI-generated notes\n"
            "✅ Professional PDF\n"
            "✅ 30 Days Validity\n\n"
            "💰 Payment system will be connected next.",
            parse_mode="Markdown",
        )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("credits", credits))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("NoteTube AI Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
