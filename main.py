from telebot.apihelper import ApiTelegramException
from hashlib import sha3_512
from os import environ, getenv
from http import HTTPStatus
from telebot.types import Message

from info_text import major
from bot import SynthesisLabsBot

environ['TOKEN'] = '6757154104:AAEdS1aEHHTj7M3yINHCWYVDEquyypQmSJg'
environ['TEST_TOKEN'] = 'test_token'
environ['TEST_CHAT_ID'] = 'test_chat_id'
environ['GROUP_CHAT_ID'] = '0000000'
environ['MAIN_CHAT_ID'] = 'main_chat_id'

TOKEN = '6757154104:AAEdS1aEHHTj7M3yINHCWYVDEquyypQmSJg'
#TEST_TOKEN = environ.get('TEST_TOKEN')
#TEST_CHAT_ID = environ.get('TEST_CHAT_ID')
GROUP_CHAT_ID = -1001674441819
#MAIN_CHAT_ID = environ.get('MAIN_CHAT_ID')

enroll_in_process = False

superusers = (900659397, 5116022329,)
super_actions = (
        ('kick', 'ban'),
        ('add', 'invite'),
        ('delete', 'clear', 'clean', 'remove'),
    )

bot = SynthesisLabsBot(token=str(TOKEN))


@bot.message_handler(commands=['start'])
def start(message, res=False):
    bot.send_message(
        message.chat.id, major['start'], reply_markup=bot.keyboard_buttons
    )


def superuser_only(func):
    def super_wrapper(*args, **kwargs):
        if bot.is_superuser:
            return func(*args, **kwargs)
    return super_wrapper


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
        ('hash', hasher),
    )

    bot.add_to_admition(message.from_user.id, bulk)


def catch_data(messages: list) -> list:
    return [x for x in messages]


def super_hasher(data: list) -> str:
    return '{hp}{sha}'.format(
        hp=major['hash_prefix'],
        sha=sha3_512(str(data).encode('utf-8')).hexdigest()
    )


def clean_denied_user_data(user_id: int) -> None:

    bot.send_message(
        GROUP_CHAT_ID, text=f'{user_id} отказано  в членстве, \
                                        рекомендуется удалить данные.'
    )


@bot.message_handler(content_types=['text'])
def handle_text(message: Message) -> None:

    global enroll_in_process

    current_chat = message.chat.id

    bot.send_message(message.chat.id, text=major[message.text][1])

    if not member(GROUP_CHAT_ID, message.from_user.id):
        if message.text == major['enroll'][0]:
            if bot.waiting_for_admition:
                bot.send_message(current_chat, text=major['enroll'][-2])
            else:
                enroll_in_process = True
                bot.id_pointer = message[-1].message_id

    if enroll_in_process:

        msg_diff = message[-1].message_id - bot.id_pointer

        qustons_count = len(major['qustons'])

        if any_button_pressed(message):

            enroll_stopped(message)
            enroll_in_process = False
        elif msg_diff == qustons_count:

            data = catch_data(messages=message[-qustons_count:])
            hasher = super_hasher(data)

            send_data_to_admin(message, data, hasher)

        bot.send_message(current_chat, text=major['qustons'][msg_diff])

    superuser_actions(message)

    bot.is_superuser = message.from_user.id in superusers


@superuser_only
def superuser_actions(message):
    super_message = message.text.split(' ')

    if any([True for x in super_actions[0] if x in super_message]):
        bot.kick_member(
            message, super_message[0], super_message[1],
            reason=super_message[3:] if len(super_message) > 3 else ''
        )
    elif any([True for x in super_actions[1] if x in super_message]):

        bot.invite_user_to_chat(message, super_message[0], super_message[1])
    elif any([True for x in super_actions[2] if x in super_message]):

        bot.clear_user_data(message.text.split()[0])


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
