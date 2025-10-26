import os
import json
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# تحميل المتغيرات البيئية
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# قاموس لحفظ file_id لكل ملف (إن استخدمت)
file_ids = {}

# مسار ملف خريطة الفيديوهات
VIDEOS_MAP_PATH = "videos_map.json"
videos_map = {}

# دوال مساعدة لقراءة وحفظ خريطة الفيديوهات
def load_videos_map():
    global videos_map
    try:
        if os.path.exists(VIDEOS_MAP_PATH):
            with open(VIDEOS_MAP_PATH, "r", encoding="utf-8") as f:
                videos_map = json.load(f)
        else:
            videos_map = {}
    except Exception:
        videos_map = {}

def save_videos_map():
    try:
        with open(VIDEOS_MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(videos_map, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# هاندلر /getid المعدل: يلتقط المعرفات من الرسالة التي تم الرد عليها
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text("📌 أرسل الأمر كرد على رسالة الفيديو للحصول على chat_id و message_id.")
        return

    # استخدم reply.chat.id و reply.message_id للحصول على القيم الصحيحة للمصدر
    chat_id = reply.chat.id
    message_id = reply.message_id

    await update.message.reply_text(f"✅ المعرفات:\nchat_id: {chat_id}\nmessage_id: {message_id}")

# دالة لنسخ رسالة الفيديو من القناة/المجموعة للمستخدم
async def send_from_storage(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str):
    entry = videos_map.get(key)
    if not entry:
        await update.message.reply_text("عذرًا، لم أجد هذا الفيديو في المخزن.")
        return
    from_chat_id = entry.get("chat_id")
    message_id = entry.get("message_id")
    try:
        await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=from_chat_id,
            message_id=message_id
        )
    except Exception:
        await update.message.reply_text("حدث خطأ أثناء استدعاء الفيديو. تأكد أن البوت مشرف في القناة/المجموعة وأن المعرفات صحيحة.")

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

    elif state == "ninth_content":
        keyboard = [
            [KeyboardButton("📚 كتب"), KeyboardButton("📘 شرح المنهاج")],
            [KeyboardButton("📄 أوراق عمل"), KeyboardButton("📝 أسئلة دورات")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("اختر نوع المحتوى للصف التاسع:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state == "ninth_specialization":
        keyboard = [
            [KeyboardButton("جبر"), KeyboardButton("هندسة")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("اختر التخصص لشرح المنهاج:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state == "algebra_units":
        keyboard = [
            [KeyboardButton("الوحدة 1"), KeyboardButton("الوحدة 2")],
            [KeyboardButton("الوحدة 3"), KeyboardButton("الوحدة 4")],
            [KeyboardButton("الوحدة 5"), KeyboardButton("الوحدة 6")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("اختر الوحدة من الجبر:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state == "geometry_units":
        keyboard = [
            [KeyboardButton("الوحدة 1"), KeyboardButton("الوحدة 2")],
            [KeyboardButton("الوحدة 3"), KeyboardButton("الوحدة 4")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("اختر الوحدة من الهندسة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state == "algebra_unit1":
        keyboard = [
            [KeyboardButton("طبيعة الأعداد")],
            [KeyboardButton("القاسم المشترك الأكبر GCD")],
            [KeyboardButton("الكسور المختزلة")],
            [KeyboardButton("الجذور التربيعية")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("وحدة جبر 1 - اختر الموضوع:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif state == "geometry_unit1":
        keyboard = [
            [KeyboardButton("التناسب")],
            [KeyboardButton("النسب المثلثية النمط الأول")],
            [KeyboardButton("النسب المثلثية النمط الثاني")],
            [KeyboardButton("النسب المثلثية النمط الثالث")],
            [KeyboardButton("النسب المثلثية النمط الرابع")],
            [KeyboardButton("⬅️ رجوع")]
        ]
        await update.message.reply_text("وحدة هندسة 1 - اختر الموضوع:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# دالة بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_keyboard(update, context, "start")

# دالة التعامل مع الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"📩 Received message: {text}")

    # إرسال ملف محفوظ عبر file_ids إن وجد
    if text in file_ids:
        await update.message.reply_document(document=file_ids[text])
        return

    # إرسال مقاطع مخزنة باستخدام خريطة الفيديوهات (copy_message من القناة/المجموعة)
    if text in videos_map:
        await send_from_storage(update, context, key=text)
        return

    if text == "📐 قسم الرياضيات":
        await show_keyboard(update, context, "math")
        return

    if text == "📘 بكالوريا":
        await show_keyboard(update, context, "baccalaureate")
        return

    if text == "📗 تاسع":
        await show_keyboard(update, context, "ninth_content")
        return

    if text == "📙 انتقالي":
        await show_keyboard(update, context, "qualifying")
        return

    if text == "📕 إعدادي":
        await show_keyboard(update, context, "preparatory")
        return

    if text == "📒 ثانوي":
        await show_keyboard(update, context, "secondary")
        return

    if text == "🧮 سابع":
        await show_keyboard(update, context, "seventh")
        return

    if text == "📊 ثامن":
        await show_keyboard(update, context, "eighth")
        return

    if text == "📈 عاشر":
        await show_keyboard(update, context, "tenth")
        return

    if text == "📉 حادي عشر":
        await show_keyboard(update, context, "eleventh")
        return

    if text == "🧪 قسم الكيمياء":
        await update.message.reply_text("📢 قسم الكيمياء قيد التطوير حالياً.")
        return

    # خيارات المحتوى لصف التاسع
    if context.user_data.get("last_state") == "ninth_content" and text in ["📚 كتب", "📘 شرح المنهاج", "📄 أوراق عمل", "📝 أسئلة دورات"]:
        if text == "📘 شرح المنهاج":
            await show_keyboard(update, context, "ninth_specialization")
        else:
            await update.message.reply_text(f"لقد اخترت: {text}.\nالمحتوى سيُضاف لاحقًا.")
        return

    # معالجة اختيارات التخصص بعد شرح المنهاج
    if context.user_data.get("last_state") == "ninth_specialization" and text in ["جبر", "هندسة"]:
        if text == "جبر":
            await show_keyboard(update, context, "algebra_units")
        else:
            await show_keyboard(update, context, "geometry_units")
        return

    # عند اختيار وحدة من الجبر
    if text.startswith("الوحدة") and context.user_data.get("last_state") == "algebra_units":
        if text.strip() == "الوحدة 1":
            await show_keyboard(update, context, "algebra_unit1")
        else:
            await update.message.reply_text("المحتوى لهذه الوحدة سيُضاف لاحقًا.")
        return

    # عند اختيار وحدة من الهندسة
    if text.startswith("الوحدة") and context.user_data.get("last_state") == "geometry_units":
        if text.strip() == "الوحدة 1":
            await show_keyboard(update, context, "geometry_unit1")
        else:
            await update.message.reply_text("المحتوى لهذه الوحدة سيُضاف لاحقًا.")
        return

    # مواضيع الوحدة الأولى من الجبر
    if text in ["طبيعة الأعداد", "القاسم المشترك الأكبر GCD", "الكسور المختزلة", "الجذور التربيعية"]:
        await update.message.reply_text(f"لقد اخترت الموضوع: {text}.\nالمحتوى قيد الإضافة.")
        return

    # مواضيع الوحدة الأولى من الهندسة
    if text in ["التناسب", "النسب المثلثية النمط الأول", "النسب المثلثية النمط الثاني", "النسب المثلثية النمط الثالث", "النسب المثلثية النمط الرابع"]:
        await update.message.reply_text(f"لقد اخترت الموضوع: {text}.\nالمحتوى قيد الإضافة.")
        return

    if text == "⬅️ رجوع":
        previous = context.user_data.get("last_state", "start")
        back_map = {
            "math": "start",
            "baccalaureate": "math",
            "ninth": "math",
            "ninth_content": "math",
            "ninth_specialization": "ninth_content",
            "algebra_units": "ninth_specialization",
            "geometry_units": "ninth_specialization",
            "algebra_unit1": "algebra_units",
            "geometry_unit1": "geometry_units",
            "qualifying": "math",
            "preparatory": "qualifying",
            "secondary": "qualifying",
            "seventh": "preparatory",
            "eighth": "preparatory",
            "tenth": "secondary",
            "eleventh": "secondary"
        }
        await show_keyboard(update, context, back_map.get(previous, "start"))
        return

    await update.message.reply_text("يرجى اختيار زر من الكيبورد.")

# دالة تسجيل Webhook لدى Telegram
def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    data = {"url": WEBHOOK_URL}
    response = requests.post(url, data=data)
    print("🔗 Webhook status:", response.text)

# دالة تشغيل البوت
def main():
    load_videos_map()

    app = ApplicationBuilder().token(TOKEN).build()

    # هاندلر مؤقت للحصول على chat_id و message_id داخل القناة/المجموعة
    app.add_handler(CommandHandler("getid", get_id))

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
