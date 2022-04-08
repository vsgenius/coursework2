from bot_api import bot_answer,longpoll
from bot_db import create_db
from vk_api.longpoll import VkEventType


def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            create_db(event.user_id)
            bot_answer(event)


if __name__ == '__main__':
    main()
