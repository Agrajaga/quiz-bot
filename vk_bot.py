import os
import random

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from quiz_api import load_quiz

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
    quiz = load_quiz("questions/1vs1201.txt")

    vk_token = os.getenv("VK_TOKEN")
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    quiz_started = False
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            if event.text == "Квиз":
                quiz_started = True
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
                continue
            if not quiz_started:
                continue
            if event.text == 'Новый вопрос':
                question = random.choice(list(quiz.keys()))
                bot_db.set(name=user_id, value=question)
                vk_api.messages.send(
                    user_id=user_id,
                    message=question,
                    random_id=random.randint(1, 1000),
                )
                continue
            if event.text == 'Сдаться':
                correct_answer = quiz.get(bot_db.get(user_id), "")
                vk_api.messages.send(
                    user_id=user_id,
                    message=f'Правильный ответ:\n{correct_answer}',
                    random_id=random.randint(1, 1000),
                )
                continue
            correct_answer = quiz.get(bot_db.get(user_id), "")
            if event.text.lower() == correct_answer.lower():
                vk_api.messages.send(
                    user_id=user_id,
                    message='Правильно! Поздравляю!',
                    random_id=random.randint(1, 1000),
                )
                continue
            vk_api.messages.send(
                user_id=user_id,
                message='Неправильно… Попробуешь ещё раз?',
                random_id=random.randint(1, 1000),
            )
