from telebot.apihelper import ApiTelegramException
from hashlib import sha3_512
from os import environ, getenv
from http import HTTPStatus
from telebot.types import Message
from pandas import read_html
from re import compile

from info_text import major
from bot import SynthesisLabsBot

environ['token'] = 'path_env'
environ['group_chat_id'] = 'path_env'

TOKEN = getenv('token')
MODERATION_CHAT_ID = -1001674441819

#TOKEN = '6757154104:AAEdS1aEHHTj7M3yINHCWYVDEquyypQmSJg'
#GROUP_CHAT_ID = -1001674441819

CITIES_URL = ('https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%')
('D0%B8%D1%81%D0%BE%D0%BA_%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D0%BE%')
('D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8')

BIRTH_VALIDATOR = '11.11.1111'
SUPERUSERS = (900659397, 5116022329, 503523768, )
SUPER_ACTIONS = (
        ('kick', 'ban'),
        ('add', 'invite'),
        ('delete', 'clear', 'clean', 'remove'),
    )

enroll_in_process = False
bot = SynthesisLabsBot(token=str(TOKEN))


@bot.message_handler(commands=['start'])
def start(message, res=False):
    bot.send_message(
        message.chat.id, major['start'], reply_markup=bot.keyboard_buttons
    )
    bot.is_superuser = message.from_user.id in SUPERUSERS
    bot.cities = read_html(CITIES_URL)[0]


def superuser_only(func):
    def super_wrapper(*args, **kwargs):
        if bot.is_superuser:
            return func(*args, **kwargs)
    return super_wrapper


def cities(cities):
    yield cities


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
        ('user_id', message.from_user.id),
        ('first_name', message.from_user.first_name),
        ('username', message.from_user.username),
        ('data', data),
        ('hash', hasher),
    )

    bot.add_to_admition(MODERATION_CHAT_ID, bulk)


def catch_data(messages: list) -> list:
    return [x for x in messages]


def super_hasher(data: list) -> str:
    return '{hp}{sha}'.format(
        hp=major['hash_prefix'],
        sha=sha3_512(str(data).encode('utf-8')).hexdigest()
    )


def clean_denied_user_data(user_id: int) -> None:

    bot.send_message(
        MODERATION_CHAT_ID, text=f'{user_id} отказано  в членстве, \
                                        рекомендуется удалить данные.'
    )


@bot.message_handler(content_types=['text'])
def handle_text(message: Message) -> None:

    global enroll_in_process

    current_chat = message.chat.id

    if not member(MODERATION_CHAT_ID, message.from_user.id):
        if message.text == major['enroll'][0]:
            if bot.waiting_for_admition:
                bot.send_message(current_chat, text=major['enroll'][-2])
            else:
                enroll_in_process = True
                bot.id_pointer = message[-1].message_id
    else:
        bot.send_message(current_chat, 'Вы уже участник')

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
    else:
        if any(map(lambda x: message.text == x.text, bot.buttons)):
            bot.send_message(current_chat, text=major[message.text][1])
        else:
            bot.send_message(current_chat, text='Неизвестная команда')


@superuser_only
@bot.message_handler(commands=[*SUPER_ACTIONS[0]])
def handle_kicks(message):

    super_message = message.text.split(' ')

    if bot.is_superuser:
        bot.kick_chat_member(
            chat_id=super_message[1],
            user_id=super_message[0],
        )
        if len(super_message) > 2:
            bot.send_message(
                chat_id=super_message[0],
                text=f'Тебя кикнули из syntlabs. Причина: {
                    super_message[2:]
                }'
            )


@superuser_only
@bot.message_handler(commands=[*SUPER_ACTIONS[1]])
def handle_add(message):

    super_message = message.text.split(' ')

    if bot.is_superuser:
        bot.send_message(
            super_message[0],
            text=bot.create_chat_invite_link(
                super_message[1]
            )
        )


@superuser_only
@bot.message_handler(commands=[*SUPER_ACTIONS[2]])
def clear_data(message):

    if bot.is_superuser:
        bot.clear_user_data(message.text)


def valid_user_form(message: Message) -> bool:

    _message = message.text.split(' ')

    name_validation = len(_message) == 3
    city_validation = _message in cities(bot.cities)
    birth_validation = compile(
        str(_message)
    ).match(
        BIRTH_VALIDATOR
    ) is not None

    if all([
        name_validation, city_validation, birth_validation
    ]):
        return True
    else:
        return False


def member(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member is not None:
            return True
        else:
            return False
    except ApiTelegramException as error:
        if error.result_json['description'] == HTTPStatus.BAD_REQUEST:
            return False


if __name__ == '__main__':
    bot.infinity_polling()
