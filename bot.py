import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    AIORateLimiter,
)
from contextlib import asynccontextmanager

# إعداد المتغيرات من البيئة
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# إنشاء تطبيق Telegram
telegram_app = Application.builder().token(TOKEN).rate_limiter(AIORateLimiter()).build()

# Lifespan لتشغيل البوت داخل FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    print("✅ Webhook تم تعيينه بنجاح")
    yield
    await telegram_app.stop()
    await telegram_app.shutdown()

# إنشاء تطبيق FastAPI
app = FastAPI(lifespan=lifespan)

# قاعدة بيانات الملفات (اختياري)
file_ids = {}

# دالة عرض الكيبورد
async def show_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, state: str):
    context.user_data["last_state"] = state
    keyboards = {
        "start": [["📐 قسم الرياضيات"], ["🧪 قسم الكيمياء"]],
        "math": [["📘 بكالوريا", "📗 تاسع"], ["📙 تأهيلي"], ["⬅️ رجوع"]],
        "baccalaureate": [["📚 كتب", "📘 شرح المنهاج"], ["📄 أوراق عمل", "📝 أسئلة دورات"], ["⬅️ رجوع"]],
        "ninth": [["📚 كتب", "📘 شرح المنهاج"], ["📄 أوراق عمل", "📝 أسئلة دورات"], ["⬅️ رجوع"]],
        "qualifying": [["📕 إعدادي", "📒 ثانوي"], ["⬅️ رجوع"]],
        "preparatory": [["🧮 سابع", "📊 ثامن"], ["⬅️ رجوع"]],
        "secondary": [["📈 عاشر", "📉 حادي عشر"], ["⬅️ رجوع"]],
        "seventh": [["📚 كتب", "📘 شرح المنهاج"], ["📄 أوراق عمل"], ["⬅️ رجوع"]],
        "eighth": [["📚 كتب", "📘 شرح المنهاج"], ["📄 أوراق عمل"], ["⬅️ رجوع"]],
        "tenth": [["📚 كتب", "📘 شرح المنهاج"], ["📄 أوراق عمل"], ["⬅️ رجوع"]],
        "eleventh": [["📚 كتب", "📘 شرح المنهاج"], ["📄 أوراق عمل"], ["⬅️ رجوع"]],
    }
    keyboard = keyboards.get(state, [["⬅️ رجوع"]])
    await update.message.reply_text("اختر:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# دالة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_keyboard(update, context, "start")

# دالة التعامل مع الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in file_ids:
        await update.message.reply_document(document=file_ids[text])
    elif text == "📐 قسم الرياضيات":
        await show_keyboard(update, context, "math")
    elif text == "📘 بكالوريا":
        await show_keyboard(update, context, "baccalaureate")
    elif text == "📗 تاسع":
        await show_keyboard(update, context, "ninth")
    elif text == "📙 تأهيلي":
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

# إضافة المعالجات
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# استقبال Webhook من Telegram على المسار /
@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return JSONResponse(content={"status": "ok"})

# مسار الفحص لـ UptimeRobot
@app.get("/ping")
def ping():
    return JSONResponse(content={"message": "pong"}, status_code=200)
