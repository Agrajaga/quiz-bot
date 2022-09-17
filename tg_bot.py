from enum import Enum, auto
import os
from functools import partial
import random

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater, ConversationHandler)

from quiz_api import load_quiz


class Status(Enum):
    CHOICE = auto()
    ATTEMPT = auto()


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    reply_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    update.message.reply_text(f'Привет {user.full_name}!',
                              reply_markup=ReplyKeyboardMarkup(
                                  reply_keyboard, resize_keyboard=True,))
    return Status.CHOICE


def handle_new_question_request(
    update: Update,
    context: CallbackContext,
    bot_db: redis.Redis,
    quiz: dict,
) -> None:
    user_id = update.effective_user.id
    question = random.choice(list(quiz.keys()))
    bot_db.set(name=user_id, value=question)
    update.message.reply_text(question)
    return Status.ATTEMPT


def handle_solution_attempt(
    update: Update,
    context: CallbackContext,
    bot_db: redis.Redis,
    quiz: dict,
) -> None:
    user_id = update.effective_user.id
    correct_answer = quiz.get(bot_db.get(user_id), "")
    if update.message.text.lower() == correct_answer.lower():
        update.message.reply_text('Правильно! Поздравляю!')
        return Status.CHOICE
    update.message.reply_text('Неправильно… Попробуешь ещё раз?')
    return Status.ATTEMPT


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
    question_request = partial(
        handle_new_question_request,
        bot_db=bot_db,
        quiz=quiz,
    )
    solution_attempt = partial(
        handle_solution_attempt,
        bot_db=bot_db,
        quiz=quiz,
    )

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Status.CHOICE: [
                MessageHandler(
                    Filters.regex('Новый вопрос'),
                    question_request
                ),
            ],
            Status.ATTEMPT: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    solution_attempt
                ),
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    dispatcher.add_handler(conversation_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
