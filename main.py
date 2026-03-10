from characters import CHARACTERS
from telegram_token import TELEGRAM_TOKEN
from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, CallbackQueryHandler, \
    MessageHandler, filters

client = OpenAI()

def character_menu():
    keyboard = [
        [InlineKeyboardButton(c["name"], callback_data=key)]
        for key, c in CHARACTERS.items()
    ]

    return InlineKeyboardMarkup(keyboard)


def change_character_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Сменить персонажа", callback_data="menu")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Выбери персонажа-переговорщика:",
        reply_markup=character_menu()
    )


async def select_character(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    character_id = query.data
    context.user_data["character"] = character_id

    await query.edit_message_text(
        f"Вы выбрали: {CHARACTERS[character_id]['name']}\n\n"
        "Теперь отправьте сообщение.",
        reply_markup=change_character_keyboard()
    )


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Выберите персонажа:",
        reply_markup=character_menu()
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "character" not in context.user_data:
        await update.message.reply_text(
            "Сначала выберите персонажа командой /start"
        )
        return

    character_id = context.user_data["character"]
    prompt = CHARACTERS[character_id]["prompt"]

    user_text = update.message.text

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text},
        ]
    )

    result = response.choices[0].message.content

    await update.message.reply_text(result, reply_markup=change_character_keyboard())


def main():

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(select_character, pattern="^(diplomat|kind|professor|chill)$"))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="menu"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен")

    app.run_polling()


if __name__ == "__main__":
    main()