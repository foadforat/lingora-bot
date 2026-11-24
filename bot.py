import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler,
    CallbackQueryHandler, ContextTypes
)

TOKEN = os.environ["BOT_TOKEN"]

users = {}

lessons = [
    "📘 درس اول: معرفی خود\n\nI am Ali. = من علی هستم.\nMy name is Sara. = اسم من سارا است.",
    "📘 درس دوم: فعل to be\n\nI am\nYou are\nHe is\nShe is\nWe are\nThey are",
    "📘 درس سوم: ضمایر\n\nI = من\nYou = تو\nHe = او\nShe = او\nWe = ما\nThey = آنها",
    "📘 درس چهارم: حال ساده\n\nI work every day.\nمن هر روز کار می‌کنم."
]

questions = [
    ("I ___ a student.", ["am", "is", "are"], 0),
    ("She ___ happy.", ["am", "is", "are"], 1),
    ("They ___ friends.", ["am", "is", "are"], 2),
    ("He ___ to school.", ["go", "goes", "going"], 1),
    ("We ___ ready.", ["is", "am", "are"], 2)
]

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

users = load_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    if uid not in users:
        users[uid] = {"level": "انتخاب نشده", "day": 0, "score": 0}
        save_users()

    keyboard = [
        [InlineKeyboardButton("A1 مبتدی", callback_data="level_A1"),
         InlineKeyboardButton("A2 مقدماتی", callback_data="level_A2")],
        [InlineKeyboardButton("B1 متوسط", callback_data="level_B1"),
         InlineKeyboardButton("B2 بالاتر از متوسط", callback_data="level_B2")],
        [InlineKeyboardButton("C1 پیشرفته", callback_data="level_C1")],
        [InlineKeyboardButton("📚 درس امروز", callback_data="lesson")],
        [InlineKeyboardButton("📝 آزمون", callback_data="quiz")],
        [InlineKeyboardButton("📊 پیشرفت من", callback_data="progress")]
    ]

    await update.message.reply_text(
        "🌍 به آکادمی Lingora خوش آمدی!\n\nسطح زبانت رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = str(query.from_user.id)
    data = query.data

    if uid not in users:
        users[uid] = {"level": "انتخاب نشده", "day": 0, "score": 0}

    if data.startswith("level_"):
        users[uid]["level"] = data.replace("level_", "")
        save_users()
        await query.message.reply_text("✅ سطح زبانت تنظیم شد.")

    elif data == "lesson":
        day = users[uid]["day"] % len(lessons)
        await query.message.reply_text(lessons[day])
        users[uid]["day"] += 1
        save_users()

    elif data == "progress":
        u = users[uid]
        await query.message.reply_text(
            f"📊 پیشرفت شما\nسطح: {u['level']}\n"
            f"درس‌ها: {u['day']}\nنمره: {u['score']}"
        )

    elif data == "quiz":
        context.user_data["question"] = 0
        context.user_data["correct"] = 0
        await send_question(query.message, context)

    elif data.startswith("answer_"):
        index = context.user_data.get("question", 0)
        answer = int(data.split("_")[1])

        if answer == questions[index][2]:
            context.user_data["correct"] += 1
            await query.message.reply_text("✅ آفرین! درست بود.")
        else:
            await query.message.reply_text("❌ پاسخ اشتباه بود.")

        index += 1
        context.user_data["question"] = index

        if index < len(questions):
            await send_question(query.message, context)
        else:
            score = context.user_data["correct"]
            users[uid]["score"] = f"{score} از 5"
            save_users()
            await query.message.reply_text(f"🏆 نمره شما: {score} از 5")

async def send_question(message, context):
    index = context.user_data["question"]
    question, options, correct = questions[index]

    keyboard = [[
        InlineKeyboardButton(option, callback_data=f"answer_{i}")
    ] for i, option in enumerate(options)]

    await message.reply_text(
        f"سؤال {index+1} از 5\n\n{question}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    port = int(os.environ.get("PORT", 10000))
    await app.bot.set_webhook(
        url=f"{os.environ['RENDER_EXTERNAL_URL']}/webhook"
    )

    from aiohttp import web

    async def webhook(request):
        data = await request.json()
        await app.update_queue.put(
            Update.de_json(data, app.bot)
        )
        return web.Response(text="OK")

    web_app = web.Application()
    web_app.router.add_post("/webhook", webhook)

    await app.initialize()
    await app.start()

    runner = web.AppRunner(web_app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    await __import__("asyncio").Event().wait()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
