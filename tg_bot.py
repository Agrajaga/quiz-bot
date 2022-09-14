import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)
from quiz_fetch import get_quiz


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    update.message.reply_text(f'Hi {user.full_name}!',
                              reply_markup=ReplyKeyboardMarkup(
                                  reply_keyboard, resize_keyboard=True))


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def handle_quiz_commands(update: Update, context: CallbackContext) -> None:
    """Handle user commands"""
    if update.message.text == 'Новый вопрос':
        question = get_quiz("questions/1vs1201.txt")[1]['question']
        update.message.reply_text(question)


def main() -> None:
    """Start the bot."""
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, handle_quiz_commands))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
