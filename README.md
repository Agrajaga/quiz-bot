# Проект: чат-бот для проведения викторин
Бот задает вопрос и ожидет ответ на него от пользователя. Пользователь может делать попытки дать правильный ответ или нажать на кнопку "Сдаться" и получить правильный ответ от бота.  
Бот для Телеграм начинает викторину после получения команды `/start`.  
Бот для VK начинает викторину после того как пользователь пришлет слово `Квиз`.


## Установка и запуск
Для работы необходим установленный Python версии 3.10  
Установите необходимые зависимости
```
pip install -r requirements.txt
```
Создайте файл `.env`, в нем разместите следующие ключи:
```
TG_TOKEN=<Токен вашего Телеграм-бота>
VK_TOKEN=<Токен вашего VK-бота>
REDIS_HOST=<Адрес облачного сервиса Redis>
REDIS_PORT=<Порт сервиса Redis>
REDIS_PASSWORD=<Пароль сервиса Redis>
```

*Подробнее*:  
* `TG_TOKEN` получать у [Отца Ботов](https://t.me/BotFather)
* `VK_TOKEN` - ключ доступа API
    - Создать свое сообщество в ВКонтакте
    - В пункте `Управление` выбрать `Работа с API`
    - Включите `Long Poll API` с типами события: Входящие сообщения
    - Создайте ключ доступа с правами: сообщения сообщества   
* `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` получать на https://redislabs.com/

Телеграм-бота запускать командой
```
python3 tg_bot.py
```
VK-бота запускать командой
```
python3 vk_bot.py
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
