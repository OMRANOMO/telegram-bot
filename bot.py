import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# تحميل المتغيرات البيئية
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# قاموس لحفظ file_id لكل ملف
file_ids = {}

# دالة عرض الكيبورد حسب الحالة
async def show_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, state: str):
    context.user_data["last_state"] = state

    if state == "start":
        keyboard = [
            [KeyboardButton("📐 قسم الرياضيات")],
            [KeyboardButton("🧪 قسم الكيمياء")]
        ]
        await update.message.reply_text("اختر القسم:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state == "math":
        keyboard = [
            [KeyboardButton("📘 بكالوريا"), KeyboardButton("📗 تاسع")],
            [KeyboardButton("📙 انتقالي")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("اختر المرحلة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state in ["baccalaureate", "ninth"]:
        keyboard = [
            [KeyboardButton("📚 كتب"), KeyboardButton("📘 شرح المنهاج")],
            [KeyboardButton("📄 أوراق عمل"), KeyboardButton("📝 أسئلة دورات")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("اختر نوع المحتوى:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state == "qualifying":
        keyboard = [
            [KeyboardButton("📕 إعدادي"), KeyboardButton("📒 ثانوي")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("اختر المستوى:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state == "preparatory":
        keyboard = [
            [KeyboardButton("🧮 سابع"), KeyboardButton("📊 ثامن")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("اختر الصف:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state == "secondary":
        keyboard = [
            [KeyboardButton("📈 عاشر"), KeyboardButton("📉 حادي عشر")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("اختر الصف:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state in ["seventh", "eighth", "tenth", "eleventh"]:
        keyboard = [
            [KeyboardButton("📚 كتب"), KeyboardButton("📘 شرح المنهاج")],
            [KeyboardButton("📄 أوراق عمل")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("اختر نوع المحتوى:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# دالة بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_keyboard(update, context, "start")

# دالة التعامل مع الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"📩 Received message: {text}")

    if text in file_ids:
        await update.message.reply_document(document=file_ids[text])

    elif text == "📐 قسم الرياضيات":
        await show_keyboard(update, context, "math")

    elif text == "📘 بكالوريا":
        await show_keyboard(update, context, "baccalaureate")

    elif text == "📗 تاسع":
        await show_keyboard(update, context, "ninth")

    elif text == "📙 انتقالي":
        await show_keyboard(update, context, "qualifying")

    elif text == "📕 إعدادي":
        await show_keyboard(update, context, "preparatory")

    elif text == "📒 ثانوي":
        await show_keyboard(update, context, "secondary")

    elif text == "🧮 سابع":
        await show_keyboard(update, context, "seventh")

    elif text == "📊 ثامن":
        await show_keyboard(update, context, "eighth")

    elif text == "📈 عاشر":
        await show_keyboard(update, context, "tenth")

    elif text == "📉 حادي عشر":
        await show_keyboard(update, context, "eleventh")

    elif text == "🧪 قسم الكيمياء":
        await update.message.reply_text("📢 قسم الكيمياء قيد التطوير حالياً.")

    elif text == "⬅️ رجوع":
        previous = context.user_data.get("last_state", "start")
        back_map = {
            "math": "start",
            "baccalaureate": "math",
            "ninth": "math",
            "qualifying": "math",
            "preparatory": "qualifying",
            "secondary": "qualifying",
            "seventh": "preparatory",
            "eighth": "preparatory",
            "tenth": "secondary",
            "eleventh": "secondary"
        }
        await show_keyboard(update, context, back_map.get(previous, "start"))

    else:
        await update.message.reply_text("يرجى اختيار زر من الكيبورد.")

# دالة تسجيل Webhook لدى Telegram
def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    data = {"url": WEBHOOK_URL}
    response = requests.post(url, data=data)
    print("🔗 Webhook status:", response.text)

# دالة تشغيل البوت
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

# نقطة البداية
if __name__ == "__main__":
    main()

