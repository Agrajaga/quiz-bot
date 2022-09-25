import os
import random

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from quiz_api import load_quiz


def user_in_quiz(func):
    def _wrapper(*args, **kwargs):
        _, db, user_id, _ = args
        user_key = f'{user_id}_quiz_started'
        if db.get(user_key):
            func(*args, **kwargs)
    return _wrapper


def start_quiz(vk_api, db, user_id):
    keyboard = VkKeyboard()
    keyboard.add_button(
        'Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)
    vk_api.messages.send(
        user_id=user_id,
        message=f'{user_id}, приветствую на нашей викторине!',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )
    user_key = f'{user_id}_quiz_started'
    db.set(user_key, 1)


@user_in_quiz
def ask_question(vk_api, db, user_id, quiz):
    question = random.choice(list(quiz.keys()))
    db.set(name=user_id, value=question)
    vk_api.messages.send(
        user_id=user_id,
        message=question,
        random_id=random.randint(1, 1000),
    )


@user_in_quiz
def get_answer(vk_api, db, user_id, quiz):
    correct_answer = quiz.get(db.get(user_id), "")
    vk_api.messages.send(
        user_id=user_id,
        message=f'Правильный ответ:\n{correct_answer}',
        random_id=random.randint(1, 1000),
    )


@user_in_quiz
def check_answer(vk_api, db, user_id, quiz):
    correct_answer = quiz.get(db.get(user_id), "")
    if event.text.lower() == correct_answer.lower():
        vk_api.messages.send(
            user_id=user_id,
            message='Правильно! Поздравляю!',
            random_id=random.randint(1, 1000),
        )
        return
    vk_api.messages.send(
        user_id=user_id,
        message='Неправильно… Попробуешь ещё раз?',
        random_id=random.randint(1, 1000),
    )


if __name__ == "__main__":
    load_dotenv()

    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_password = os.getenv("REDIS_PASSWORD")
    bot_db = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True,
    )
    quiz_filename = os.getenv('QUIZ_FILENAME')
    quiz = load_quiz(quiz_filename)

    vk_token = os.getenv("VK_TOKEN")
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            if event.text == "Квиз":
                start_quiz(vk_api, bot_db, user_id)
            elif event.text == 'Новый вопрос':
                ask_question(vk_api, bot_db, user_id, quiz)
            elif event.text == 'Сдаться':
                get_answer(vk_api, bot_db, user_id, quiz)
            else:
                check_answer(vk_api, bot_db, user_id, quiz)
