from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

import gspread
from oauth2client.service_account import ServiceAccountCredentials

ADMIN_ID = 612855589

def save_to_sheet(user, data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1JBM4dMlEuDYyU9_2w6iOOFEhrIV8XDPNCg_ph_MTrLc").worksheet("Лист1")
    all_rows = sheet.get_all_values()
    next_number = len(all_rows) + 1

    row = [
        next_number,
        user.id,
        f"@{user.username}" if user.username else "немає",
        data.get("age", ""),
        data.get("device", ""),
        data.get("stream", ""),
        data.get("motivation", ""),
        data.get("crypto", ""),
        ""
    ]

    sheet.append_row(row)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [["✅ Я готовий(-а) пройти опитування"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Привіт, {user.first_name}! 👋\n\n"
        "Ласкаво просимо до проєкту *STREAMERS GUN*!\n\n"
        "Цей бот допоможе тобі пройти короткий відбір для участі.\n\n"
        "Коли будеш готовий(-а) — натисни кнопку нижче.",
        parse_mode="Markdown",
        reply_markup=markup
    )

async def handle_ready(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["18-20"], ["20-25"], ["25-30"], ["30-40"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Скажи, будь ласка, скільки тобі років?\nВибери свій варіант нижче 👇",
        reply_markup=markup
    )
    context.user_data["step"] = "age"

async def handle_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    keyboard = [["✅ Так, є ПК або ноутбук"], ["📱 Тільки телефон"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Чи є у тебе комп’ютер або ноутбук?", reply_markup=markup)
    context.user_data["step"] = "device"

async def handle_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    context.user_data["device"] = answer
    if answer == "📱 Тільки телефон":
        await update.message.reply_text("❌ Вибач, друже, але ти нам поки не підходиш…")
        return
    keyboard = [["✅ Так, готовий(-а)!"], ["❌ Ні, не готовий(-а)"], ["🙂 Буду старатись!"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Чи готовий(-а) стрімити мінімум 2 години на день?", reply_markup=markup)
    context.user_data["step"] = "stream"

async def handle_stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    context.user_data["stream"] = answer
    if answer in ["❌ Ні, не готовий(-а)"]:
        await update.message.reply_text("🙏 Дякуємо за чесність! Але ми шукаємо саме тих, хто вже повністю готовий. Бажаємо тобі успіхів!")
        return
    keyboard = [["💸 Гроші"], ["🚀 Популярність"], ["🎯 Інтерес"], ["💡 Самореалізація"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Чому ти хочеш стрімити казино в TikTok?", reply_markup=markup)
    context.user_data["step"] = "why"

async def handle_why(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["motivation"] = update.message.text
    keyboard = [
        ["✅ Так, маю досвід"],
        ["👛 Користувався(-лась) біржею раз або два"],
        ["🤷 Чув(-ла), але не користувався(-лась)"],
        ["❓ Що таке USDT?"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Маєш досвід із криптовалютою?\nМи виплачуємо зарплату в *USDT 💵*", parse_mode="Markdown", reply_markup=markup)
    context.user_data["step"] = "crypto"

async def handle_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    context.user_data["crypto"] = answer
    user = update.effective_user

    if answer == "✅ Так, маю досвід":
        await update.message.reply_text("🎉 Готово! Дякую, що пройшов(-ла) опитування! З тобою зв’яжеться менеджер команди 📩")
    else:
        keyboard = [["Зрозумів 🧠"]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "💸 *Зарплата у USDT — це просто:*\n\n"
            "USDT — це стабільна криптовалюта, яка завжди дорівнює 1 долару США.\nТобто 100 USDT ≈ 100$.\n\n"
            "🔐 Ти отримуєш зарплату в USDT на біржу (наприклад: Binance, WhiteBit, Bybit).\n\n"
            "💳 Потім одним кліком можеш:\n • 🔁 Обміняти на гривні/євро\n • 💸 Вивести прямо на свою банківську картку\n • 💼 Зберігати як «електронний долар»\n\n"
            "🧠 Це швидко, зручно і легально. Ми допоможемо, якщо ти новачок.",
            parse_mode="Markdown",
            reply_markup=markup
        )
        context.user_data["step"] = "done"
        return

    message = f"📝 Нова заявка від кандидата:\nUsername: @{user.username if user.username else 'немає'}\nID: {user.id}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    save_to_sheet(user, context.user_data)

async def handle_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text("🎉 Дякую, що пройшов(-ла) опитування! З тобою зв’яжеться менеджер команди 📩")
    message = f"📝 Нова заявка від кандидата:\nUsername: @{user.username if user.username else 'немає'}\nID: {user.id}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    save_to_sheet(user, context.user_data)


def main():
    app = Application.builder().token("7262689907:AAGej4aFkZo8plN16IGeS_5JDx8YuGyaGK4").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^✅ Я готовий\(-а\) пройти опитування$"), handle_ready))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(18-20|20-25|25-30|30-40)$"), handle_age))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(✅ Так, є ПК або ноутбук|📱 Тільки телефон)$"), handle_device))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(✅ Так, готовий\(-а\)!|❌ Ні, не готовий\(-а\)|🙂 Буду старатись!)$"), handle_stream))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(💸 Гроші|🚀 Популярність|🎯 Інтерес|💡 Самореалізація)$"), handle_why))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(✅ Так, маю досвід|👛 Користувався\(-лась\) біржею раз або два|🤷 Чув\(-ла\), але не користувався\(-лась\)|❓ Що таке USDT\?)$"), handle_crypto))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Зрозумів 🧠$"), handle_done))
    app.run_polling()

if __name__ == "__main__":
    main()
