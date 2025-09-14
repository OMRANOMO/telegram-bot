import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.ext import AIORateLimiter
import asyncio

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

file_ids = {}

# إعداد FastAPI
app = FastAPI()

# إنشاء تطبيق Telegram
telegram_app = Application.builder().token(TOKEN).rate_limiter(AIORateLimiter()).build()

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
            [KeyboardButton("📙 تأهيلي")],
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_keyboard(update, context, "start")

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

# إعداد المسارات في FastAPI
@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return JSONResponse(content={"status": "ok"})

@app.get("/ping")
def ping():
    return JSONResponse(content={"message": "pong"}, status_code=200)

# إعداد البوت
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# تعيين Webhook عند التشغيل
@app.on_event("startup")
async def on_startup():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    data = {"url": WEBHOOK_URL}
    response = requests.post(url, data=data)
    print("🔗 Webhook status:", response.text)
