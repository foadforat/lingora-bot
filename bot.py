import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
ApplicationBuilder, CommandHandler,
CallbackQueryHandler, ContextTypes
)

TOKEN = os.environ["9174864856:AAHhBOcmJ77xiH4yQwX6qE4ZhLYvg_gKKTc"]
FILE = "users.json"

def load_users():
if os.path.exists(FILE):
with open(FILE, "r") as f:
return json.load(f)
return {}

users = load_users()

def save_users():
with open(FILE, "w") as f:
json.dump(users, f)

lessons = [
"📘 درس اول: معرفی خود\n\nI am Ali. = من علی هستم.\nMy name is Sara. = اسم من سارا است.\n\nلغات:\nName = نام\nStudent = دانش‌آموز\nTeacher = معلم",
"📘 درس دوم: فعل to be\n\nI am\nYou are\nHe is\nShe is\nWe are\nThey are\n\nمثال:\nShe is happy. = او خوشحال است.",
"📘 درس سوم: ضمایر\n\nI = من\nYou = تو\nHe = او (مذکر)\nShe = او (مونث)\nWe = ما\nThey = آنها\n\nمثال:\nThey are friends.",
"📘 درس چهارم: زمان حال ساده\n\nI work every day.\nمن هر روز کار می‌کنم.\n\nShe works every day.\nاو هر روز کار می‌کند.\n\nنکته: برای He و She معمولاً به فعل s اضافه می‌کنیم."
]

questions = [
("I ___ a student.", ["am", "is", "are"], 0),
("She ___ happy.", ["am", "is", "are"], 1),
("They ___ friends.", ["am", "is", "are"], 2),
("He ___ to school.", ["go", "goes", "going"], 1),
("We ___ ready.", ["is", "am", "are"], 2)
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = str(update.effective_user.id)

if uid not in users: users[uid] = {"level": "انتخاب نشده", "day": 0, "score": 0} save_users() keyboard = [ [InlineKeyboardButton("A1 مبتدی", callback_data="level_A1"), InlineKeyboardButton("A2 مقدماتی", callback_data="level_A2")], [InlineKeyboardButton("B1 متوسط", callback_data="level_B1"), InlineKeyboardButton("B2 بالاتر از متوسط", callback_data="level_B2")], [InlineKeyboardButton("C1 پیشرفته", callback_data="level_C1")], [InlineKeyboardButton("📚 درس امروز", callback_data="lesson")], [InlineKeyboardButton("📝 آزمون", callback_data="quiz")], [InlineKeyboardButton("📊 پیشرفت من", callback_data="progress")] ] await update.message.reply_text( "🌍 به آکادمی Lingora خوش آمدی!\n\nسطح زبانت رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard) ) 

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

uid = str(query.from_user.id) data = query.data if uid not in users: users[uid] = {"level": "انتخاب نشده", "day": 0, "score": 0} if data.startswith("level_"): level = data.replace("level_", "") users[uid]["level"] = level save_users() await query.message.reply_text( f"✅ سطح شما با موفقیت روی {level} تنظیم شد!\n\n" "برای دریافت درس روی 📚 درس امروز بزن." ) elif data == "lesson": day = users[uid]["day"] % len(lessons) await query.message.reply_text(lessons[day]) users[uid]["day"] += 1 save_users() elif data == "progress": u = users[uid] await query.message.reply_text( f"📊 گزارش پیشرفت شما در Lingora\n\n" f"سطح: {u['level']}\n" f"درس‌های دریافت‌شده: {u['day']}\n" f"آخرین نمره آزمون: {u['score']}" ) elif data == "quiz": context.user_data["question"] = 0 context.user_data["correct"] = 0 await send_question(query.message, context) elif data.startswith("answer_"): index = context.user_data.get("question", 0) answer = int(data.split("_")[1]) if answer == questions[index][2]: context.user_data["correct"] += 1 await query.message.reply_text("✅ آفرین! پاسخ درست بود.") else: correct = questions[index][1][questions[index][2]] await query.message.reply_text( f"❌ پاسخ درست: {correct}" ) index += 1 context.user_data["question"] = index if index < len(questions): await send_question(query.message, context) else: score = context.user_data["correct"] users[uid]["score"] = f"{score} از {len(questions)}" save_users() await query.message.reply_text( f"🏆 آزمون تمام شد!\n\n" f"نمره شما: {score} از {len(questions)}" ) 

async def send_question(message, context):
index = context.user_data["question"]
question, options, correct = questions[index]

keyboard = [[ InlineKeyboardButton( f"{chr(65+i)}) {option}", callback_data=f"answer_{i}" ) ] for i, option in enumerate(options)] await message.reply_text( f"سؤال {index+1} از {len(questions)}\n\n{question}", reply_markup=InlineKeyboardMarkup(keyboard) ) 

async def main():
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start)) app.add_handler(CallbackQueryHandler(buttons)) print("LINGORA IS RUNNING!") await app.initialize() await app.start() await app.updater.start_polling() await __import__("asyncio").Event().wait() 

if name == "main":
import asyncio
asyncio.run(main())

