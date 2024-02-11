from typing import Any, Optional
from telebot.apihelper import ApiTelegramException
from hashlib import sha3_512
from os import environ, getenv
from http import HTTPStatus
from telebot.types import Message

from info_text import major
from bot import SynthesisLabsBot

environ['TOKEN'] = 'token'
environ['TEST_TOKEN'] = 'test_token'
environ['TEST_CHAT_ID'] = 'test_chat_id'
environ['GROUP_CHAT_ID'] = '0000000'
environ['MAIN_CHAT_ID'] = 'main_chat_id'

TOKEN = getenv('TOKEN')
TEST_TOKEN = environ.get('TEST_TOKEN')
TEST_CHAT_ID = environ.get('TEST_CHAT_ID')
GROUP_CHAT_ID = environ.get('GROUP_CHAT_ID')
MAIN_CHAT_ID = environ.get('MAIN_CHAT_ID')

enroll_in_process = False

superusers = (900659397, 5116022329,)

bot = SynthesisLabsBot(token=str(TOKEN))


@bot.message_handler(commands=['start'])
def start(message, res=False):
    bot.send_message(
        message.chat.id, major['start'], reply_markup=bot.keyboard_buttons
    )


def any_button_pressed(message) -> bool:
    return any(list(map(
        lambda x: True if x[0] == message.text else False,
        major.values()
    )))


def enroll_stopped(message) -> None:
    bot.send_message(
        message.from_user.id, 'Заполнение анкеты приостановлено. \
                                Вы сможете продолжить позднее.'
    )


def send_data_to_admin(message: Message, data: list, hasher: str) -> None:

    bulk = (
        ('chat_id', message.chat.id),
        ('first_name', message.from_user.first_name),
        ('username', message.from_user.username),
        ('data', data),
        ('hash', hasher)
    )

    bot.add_to_admition(message.from_user.id, bulk)


def catch_data(messages: list) -> list:
    return [x for x in messages]


def super_hasher(data: list) -> str:
    return '{hp}{sha}'.format(
        hp=major['hash_prefix'],
        sha=sha3_512(str(data).encode('utf-8')).hexdigest()
    )


def is_super_user(member_id: int) -> bool:

    return True if member_id in superusers else False


def clean_denied_user_data(user_id: int) -> None:

    bot.send_message(
        TEST_CHAT_ID, text=f'{user_id} отказано  в членстве, \
                                        рекомендуется удалить данные.'
    )


@bot.message_handler(content_types=['text'])
def handle_text(message: Message) -> None:

    current_chat = message.chat.id

    if not member(GROUP_CHAT_ID, message.from_user.id):
        if message.text == major['enroll'][0]:
            if bot.waiting_for_admition:
                bot.send_message(current_chat, text=major['enroll'][-2])
            else:
                enroll_in_process = True
                bot.id_pointer = message[-1].message_id

    if enroll_in_process:

        msg_diff = message[-1].message_id - bot.id_pointer

        id_slice = len(major['qustons'])

        if any_button_pressed(message):

            enroll_stopped(message)
            enroll_in_process = False
        elif msg_diff == id_slice:

            data = catch_data(messages=message[-id_slice:])
            hasher = super_hasher(data)

            send_data_to_admin(message, data, hasher)

        bot.send_message(current_chat, text=major['qustons'][msg_diff])

    if is_super_user(message.from_user.id):
        super_message = message.text.split(' ')
        if 'kick' in super_message:
            bot.kick_member(
                message=message,
                user_id=super_message[0],
                chat_id=super_message[1],
                reason=super_message[3:] if len(super_message) > 3 else ''
            )
        elif 'add' in super_message:
            bot.invite_user_to_chat(
                message=message,
                user_chat_id=super_message[0],
                chat_id=super_message[1]
            )

    bot.is_superuser = True if is_super_user(message.from_user.id) else False


def member(chat_id, user_id):
    try:
        bot.get_chat_member(chat_id, user_id)
        bot.send_message(chat_id, 'Вы уже наняты')
        return True
    except ApiTelegramException as error:
        if error.result_json['description'] == HTTPStatus.BAD_REQUEST:
            return False


if __name__ == '__main__':
    bot.infinity_polling()
