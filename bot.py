import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

file_ids = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📐 قسم الرياضيات")],
        [KeyboardButton("🧪 قسم الكيمياء")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("اختر القسم:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text in file_ids:
        await update.message.reply_document(document=file_ids[text])
    elif text == "📐 قسم الرياضيات":
        keyboard = [
            [KeyboardButton("📘 بكالوريا"), KeyboardButton("📗 تاسع")],
            [KeyboardButton("📙 تأهيلي")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("اختر المرحلة:", reply_markup=reply_markup)

    elif text in ["📘 بكالوريا", "📗 تاسع"]:
        keyboard = [
            [KeyboardButton("📚 كتب"), KeyboardButton("📘 شرح المنهاج")],
            [KeyboardButton("📄 أوراق عمل"), KeyboardButton("📝 أسئلة دورات")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("اختر نوع المحتوى:", reply_markup=reply_markup)

    elif text == "📙 تأهيلي":
        keyboard = [
            [KeyboardButton("📕 إعدادي"), KeyboardButton("📒 ثانوي")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("اختر المستوى:", reply_markup=reply_markup)

    elif text == "📕 إعدادي":
        keyboard = [
            [KeyboardButton("🧮 سابع"), KeyboardButton("📊 ثامن")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("اختر الصف:", reply_markup=reply_markup)

    elif text == "📒 ثانوي":
        keyboard = [
            [KeyboardButton("📈 عاشر"), KeyboardButton("📉 حادي عشر")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("اختر الصف:", reply_markup=reply_markup)

    elif text in ["🧮 سابع", "📊 ثامن", "📈 عاشر", "📉 حادي عشر"]:
        keyboard = [
            [KeyboardButton("📚 كتب"), KeyboardButton("📘 شرح المنهاج")],
            [KeyboardButton("📄 أوراق عمل")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("اختر نوع المحتوى:", reply_markup=reply_markup)

    elif text == "🧪 قسم الكيمياء":
        await update.message.reply_text("📢 قسم الكيمياء قيد التطوير حالياً.")

    elif text == "⬅️ رجوع":
        await start(update, context)

    else:
        await update.message.reply_text("يرجى اختيار زر من الكيبورد.")

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    data = {"url": WEBHOOK_URL}
    response = requests.post(url, data=data)
    print("🔗 Webhook status:", response.text)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ البوت يعمل الآن عبر Webhook...")
    set_webhook()

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
