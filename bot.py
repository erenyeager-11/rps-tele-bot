# 🎮 Telegram Stone Paper Scissors Bot (Buttons + Topics Supported)
# Minimal • Smooth • Works in topic-divided groups • 24x7 hosted

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import random

TOKEN = os.getenv("TOKEN")
# Data storage (chat_id + topic_id based)
choices = {}   # {(chat_id, topic_id): {user_id: choice}}
scores = {}    # {(chat_id, topic_id): {user_id: points}}

TASKS = [
    "Send a funny sticker 😂",
    "Say sorry in the group 😌",
    "Send a motivational quote 💪",
    "Type: I accept my defeat 🤝",
    "Stay silent for 10 minutes 🤐"
]

# ---------- START COMMAND ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    topic_id = update.message.message_thread_id  # supports topics

    keyboard = [[
        InlineKeyboardButton("🪨 Rock", callback_data="rock"),
        InlineKeyboardButton("📄 Paper", callback_data="paper"),
        InlineKeyboardButton("✂️ Scissors", callback_data="scissors")
    ]]

    await update.message.reply_text(
        "🎮 *Stone Paper Scissors*\nChoose your move 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
        message_thread_id=topic_id
    )

# ---------- BUTTON HANDLER ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    topic_id = query.message.message_thread_id
    user = query.from_user
    choice = query.data

    key = (chat_id, topic_id)
    choices.setdefault(key, {})[user.id] = choice

    if len(choices[key]) < 2:
        await query.edit_message_text(
            f"{user.first_name} locked in 🔒\nWaiting for opponent..."
        )
        return

    # Take first two players
    players = list(choices[key].items())[:2]
    (u1, c1), (u2, c2) = players

    def decide(a, b):
        if a == b:
            return 0
        if (a == "rock" and b == "scissors") or \
           (a == "paper" and b == "rock") or \
           (a == "scissors" and b == "paper"):
            return 1
        return 2

    result = decide(c1, c2)

    scores.setdefault(key, {}).setdefault(u1, 0)
    scores.setdefault(key, {}).setdefault(u2, 0)

    if result == 0:
        text = "🤝 *It's a Draw!* No points awarded."
    else:
        winner = u1 if result == 1 else u2
        loser = u2 if result == 1 else u1

        scores[key][winner] += 5
        task = random.choice(TASKS)

        text = (
            f"🏆 *Winner:* <a href='tg://user?id={winner}'>User</a>\n"
            f"😢 *Loser:* <a href='tg://user?id={loser}'>User</a>\n"
            f"➕ *+5 Points* awarded\n\n"
            f"📝 *Task for loser:* {task}"
        )

    choices[key].clear()
    await query.edit_message_text(text, parse_mode="HTML")

# ---------- SCORE COMMAND ----------
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    topic_id = update.message.message_thread_id
    key = (chat_id, topic_id)

    if key not in scores:
        await update.message.reply_text(
            "📊 No scores yet",
            message_thread_id=topic_id
        )
        return

    msg = "🏅 <b>Scoreboard</b>\n\n"
    for uid, pts in scores[key].items():
        msg += f"<a href='tg://user?id={uid}'>User</a> → {pts} points\n"

    await update.message.reply_text(
        msg,
        parse_mode="HTML",
        message_thread_id=topic_id
    )

# ---------- APP ----------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("score", score))

app.run_polling()


