import os
import json
import threading
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import run  # خادم Flask الوهمي

# مفتاح البوت و رابط Webhook
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# قاموس لحفظ file_id لكل ملف
file_ids = {}

# مسارات ملفات PDF (يفضل لاحقًا رفعها إلى GitHub أو تخزينها في مكان عام)
pdf_paths = {
    "📚 الدورات": "file.pdf",
    "📄 أوراق عمل": "file.pdf",
    "الوحدة 1": "file.pdf",
    "الوحدة 2": "file.pdf",
    "الوحدة 3": "file.pdf",
    "الوحدة 4": "file.pdf",
    "الوحدة 5": "file.pdf",
    "الوحدة 6": "file.pdf"
}

# دالة بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📚 الدورات")],
        [KeyboardButton("📄 أوراق عمل")],
        [KeyboardButton("📘 شرح المنهاج")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("اختر أحد الخيارات التالية:", reply_markup=reply_markup)

# دالة التعامل مع الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text in pdf_paths:
        if text in file_ids:
            await update.message.reply_document(document=file_ids[text])
        else:
            try:
                with open(pdf_paths[text], "rb") as f:
                    msg = await update.message.reply_document(document=f)
                    file_ids[text] = msg.document.file_id
            except Exception as e:
                await update.message.reply_text("حدث خطأ أثناء إرسال الملف.")
                print(f"❌ خطأ: {e}")

    elif text == "📘 شرح المنهاج":
        keyboard = [
            [KeyboardButton("الوحدة 1"), KeyboardButton("الوحدة 2")],
            [KeyboardButton("الوحدة 3"), KeyboardButton("الوحدة 4")],
            [KeyboardButton("الوحدة 5"), KeyboardButton("الوحدة 6")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("اختر الوحدة:", reply_markup=reply_markup)

    elif text == "⬅️ رجوع":
        await start(update, context)

    else:
        await update.message.reply_text("يرجى اختيار زر من الكيبورد.")

# تشغيل البوت باستخدام Webhook
def main():
    threading.Thread(target=run).start()  # تشغيل خادم Flask في الخلفية

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ البوت يعمل الآن عبر Webhook...")

app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),  # استخدام المنفذ الديناميكي
    webhook_url=WEBHOOK_URL
)


import requests

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    data = {"url": WEBHOOK_URL}
    response = requests.post(url, data=data)
    print("🔗 Webhook status:", response.text)

set_webhook()




if __name__ == "__main__":
    main()




