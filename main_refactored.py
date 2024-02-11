from typing import Any, Optional
from telebot.apihelper import ApiTelegramException
from hashlib import sha3_512
from os import environ, getenv
from http import HTTPStatus

from info_text import major
from bot import SynthesisLabsBot

environ['TOKEN'] = 'token'
environ['TEST_TOKEN'] = 'test_token'
environ['TEST_CHAT_ID'] = 'test_chat_id'
environ['GROUP_CHAT_ID'] = 'group_chat_id'
environ['MAIN_CHAT_ID'] = 'main_chat_id'

TOKEN = getenv('TOKEN')
TEST_TOKEN = environ.get('TEST_TOKEN')
TEST_CHAT_ID = environ.get('TEST_CHAT_ID')
GROUP_CHAT_ID = environ.get('GROUP_CHAT_ID')
MAIN_CHAT_ID = environ.get('MAIN_CHAT_ID')

enroll_in_process = False

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


def send_data_to_admin(message, data, hasher):
    bot.send_message(
        chat_id=TEST_CHAT_ID,
        text=str({
            'chat_id': message.chat.id,
            'first_name': message.from_user.first_name,
            'username': message.from_user.username,
            'data': data,
            'hash': hasher
            })
        )


def catch_data(messages):
    return [x for x in messages]


def super_hasher(data):
    return '{hp}{sha}'.format(
        hp=major['hash_prefix'],
        sha=sha3_512(data.encode('utf-8')).hexdigest()
    )


@bot.message_handler(content_types=['text'])
def handle_text(message):

    current_chat = message.chat.id

    if not member(GROUP_CHAT_ID, message.from_user.id):
        bot.send_message(current_chat, major['enroll'][2])

        if message.text == major['enroll'][0]:
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
            hasher = super_hasher(major)

            send_data_to_admin(message, data, hasher)

        bot.send_message(current_chat, text=major['qustons'][msg_diff])

    bot.send_message(current_chat, text=major[message.text][1])


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
