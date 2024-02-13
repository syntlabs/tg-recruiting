from telebot.apihelper import ApiTelegramException
from hashlib import sha3_512
from os import environ, getenv
from http import HTTPStatus
from telebot.types import Message
from pandas import read_html
from re import findall

from info_text import major
from bot import SynthesisLabsBot

#environ['token'] = 'path_env'
#environ['group_chat_id'] = 'path_env'
#environ['cities_list'] = 'path_ro_cities'

cities_list = (
    'Москва',
    'Рязань',
    'Петушки',
    'Фашингтон',
    'село Париж, московская область',
)

MODERATION_CHAT_ID = -1001674441819
PUBLIC_CHAT = -1001853428617

TOKEN = '6757154104:AAEdS1aEHHTj7M3yINHCWYVDEquyypQmSJg'

BIRTH_VALIDATOR = '11.11.1111'
SUPERUSERS = (900659397, 5116022329, 503523768, )
SUPER_ACTIONS = (
        ('kick', 'ban'),
        ('add', 'invite'),
        ('delete', 'clear', 'clean', 'remove'),
    )

shift = -1

enroll_in_process = False
bot = SynthesisLabsBot(token=str(TOKEN))
qustons_copy = dict()
qustons_copy['qustons'] = list(major['qustons'])


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
    current_user = message.from_user.id
    msg = message.text
    bot.is_superuser = message.from_user.id in SUPERUSERS

    if not member(current_user):

        if not enroll_in_process:
            if msg == 'Вступить' and not bot.waiting_for_admition:
                bot.send_message(current_chat, text=major['Вступить'][1])
                enroll_in_process = True
            elif msg == 'Вступить' and bot.waiting_for_admition:
                bot.send_message(current_chat, text=major['Вступить'][2])
            elif any([True for x in major.keys() if x == msg]):
                bot.send_message(current_chat, major[msg][1])
            else:
                bot.send_message(current_chat, text='Неизвестная команда')
        else:
            process_enrollment(message)


def process_enrollment(message):

    global enroll_in_process

    if len(qustons_copy['qustons']) == 0:
        bot.send_message(
            message.chat.id, text='Заявка заполнена, ожидайте ответ'
        )
        bot.waiting_for_admition = True
        enroll_in_process = False
    else:
        bot.send_message(message.chat.id, text=qustons_copy['qustons'][0])
        del qustons_copy['qustons'][0]


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


def valid_step(message: Message) -> bool:

    scalp_message = message.text.split('')

    name_valid = len(scalp_message) == 3
    birth_valid = findall(BIRTH_VALIDATOR, message.text)
    city_valid = message.text.lower() in cities_list

    if message[-1].text.lower() == 'фио' and name_valid:
        return True
    elif message[-1].text.lower() == 'дата рождения' and birth_valid:
        return True
    elif message[-1].text.lower() == 'город' and city_valid:
        return True
    else:
        return False


def member(user_id):
    try:
        member = bot.get_chat_member(PUBLIC_CHAT, user_id)
        if member is not None:
            return True
        else:
            return False
    except ApiTelegramException as error:
        if error.result_json['description'] == HTTPStatus.BAD_REQUEST:
            return False


if __name__ == '__main__':
    bot.infinity_polling()
