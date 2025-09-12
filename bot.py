from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# مفتاح البوت
TOKEN = "8310092576:AAFWsFfaL9eiTbaryNqpT3tilbTFL5h2br4"

# قاموس لحفظ file_id لكل ملف
file_ids = {}

# مسارات ملفات PDF
pdf_paths = {
    "📚 الدورات": "D:/boot/pdf/file.pdf",
    "📄 أوراق عمل": "D:/boot/pdf/file.pdf",
    "الوحدة 1": "D:/boot/pdf/file.pdf",
    "الوحدة 2": "D:/boot/pdf/file.pdf",
    "الوحدة 3": "D:/boot/pdf/file.pdf",
    "الوحدة 4": "D:/boot/pdf/file.pdf",
    "الوحدة 5": "D:/boot/pdf/file.pdf",
    "الوحدة 6": "D:/boot/pdf/file.pdf"
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
        # إذا كان لدينا file_id محفوظ، نستخدمه مباشرة
        if text in file_ids:
            await update.message.reply_document(document=file_ids[text])
        else:
            try:
                with open(pdf_paths[text], "rb") as f:
                    msg = await update.message.reply_document(document=f)
                    # حفظ file_id بعد أول إرسال
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

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
