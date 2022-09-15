import os
from functools import partial
import random

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

from quiz_api import load_quiz


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    update.message.reply_text(f'Привет {user.full_name}!',
                              reply_markup=ReplyKeyboardMarkup(
                                  reply_keyboard, resize_keyboard=True,))


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def handle_quiz_commands(
    update: Update,
    context: CallbackContext,
    bot_db: redis.Redis,
    quiz: dict,
) -> None:
    """Handle user commands"""
    user_id = update.effective_user.id
    if update.message.text == 'Новый вопрос':
        question = random.choice(list(quiz.keys()))
        bot_db.set(name=user_id, value=question)
        update.message.reply_text(question)
        return
    if update.message.text == 'Сдаться':
        return
    if update.message.text == 'Мой счет':
        return
    correct_answer = quiz.get(bot_db.get(user_id), "")
    if update.message.text.lower() == correct_answer.lower():
        update.message.reply_text('Правильно! Поздравляю!')
        return
    update.message.reply_text('Неправильно… Попробуешь ещё раз?')


def main() -> None:
    """Start the bot."""
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_password = os.getenv("REDIS_PASSWORD")

    updater = Updater(tg_token)
    bot_db = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True,
    )

    dispatcher = updater.dispatcher

    quiz = load_quiz("questions/1vs1201.txt")
    quiz_handler = partial(
        handle_quiz_commands,
        bot_db=bot_db,
        quiz=quiz,
    )

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, quiz_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
