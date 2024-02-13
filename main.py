from telebot.apihelper import ApiTelegramException
from hashlib import sha3_512
from os import environ, getenv
from http import HTTPStatus
from telebot.types import Message

from info_text import major
from bot import SynthesisLabsBot

#environ['token'] = 'path_env'
#environ['group_chat_id'] = 'path_env'
#environ['cities_list'] = 'path_ro_cities'

#TOKEN = getenv('token')
#MODERATION_CHAT_ID = getenv('moderation_chat_id')
#PUBLIC_CHAT_ID = getenv('public_chat_id')

MODERATION_CHAT_ID = -1001674441819
PUBLIC_CHAT_ID = -1001853428617

TOKEN = '6757154104:AAEdS1aEHHTj7M3yINHCWYVDEquyypQmSJg'

SUPERUSERS = (900659397, 5116022329, 503523768, )
SUPER_ACTIONS = (
        ('kick', 'ban'),
        ('add', 'invite'),
        ('delete', 'clear', 'clean', 'remove'),
    )

enroll_in_process = False

bot = SynthesisLabsBot(token=str(TOKEN))

qustons_copy = dict()
data_container = dict()

qustons_copy['qustons'] = list(major['qustons'])


def any_button_pressed(message: Message) -> bool:
    return any(
        list(
            map(
                lambda x: x[0] == message.text,
                major.keys()
            )
        )
    )


def enroll_stopped(message: Message) -> None:
    bot.send_message(
        message.from_user.id, 'Заполнение анкеты приостановлено. \
                                Вы сможете продолжить позднее.'
    )


def super_hasher(data: dict) -> str:
    return '{hp}{sha}'.format(
        hp=major['hash_prefix'],
        sha=sha3_512(
            str(
                data
            ).encode('utf-8')
        ).hexdigest()
    )


def member(user_id: int) -> bool:
    try:
        bot.get_chat_member(PUBLIC_CHAT_ID, user_id)
    except ApiTelegramException as error:
        if error.result_json['description'] == HTTPStatus.BAD_REQUEST:
            return False
    else:
        return True
    finally:
        return False


def process_enrollment(message: Message):

    global enroll_in_process

    if len(qustons_copy['qustons']) == 0:

        bot.waiting_for_admition = True
        enroll_in_process = False

        bot.send_message(
            message.chat.id, text='Заявка заполнена, ожидайте ответ'
        )

        bot.add_to_admition(
            message.from_user.id, (
                ('user_id', message.from_user.id),
                ('first_name', message.from_user.first_name),
                ('username', message.from_user.username),
                ('data', data_container),
                ('hash', super_hasher(data_container)),
            )
        )
    else:
        pointer = qustons_copy['qustons'][0]
        data_container[pointer] = message.text.encode('utf-8')

        bot.send_message(message.chat.id, text=pointer)

        del qustons_copy['qustons'][0]


@bot.message_handler(commands=['start'])
def start(message: Message, res=False) -> None:
    bot.send_message(
        message.chat.id, major['start'], reply_markup=bot.keyboard_buttons
    )


@bot.message_handler(content_types=['text'])
def handle_text(message: Message) -> None:

    global enroll_in_process

    current_chat = message.chat.id
    current_user = message.from_user.id
    msg = message.text
    bot.is_superuser = True if message.from_user.id in SUPERUSERS else False

    if not member(current_user):

        if not enroll_in_process:

            if msg == 'Вступить' and not bot.waiting_for_admition:
                bot.send_message(current_chat, text=major['Вступить'][1])
                enroll_in_process = True

            elif msg == 'Вступить' and bot.waiting_for_admition:
                bot.send_message(current_chat, text=major['Вступить'][2])

            elif any_button_pressed(message):
                bot.send_message(current_chat, major[msg][1])

            else:
                bot.send_message(current_chat, text='Неизвестная команда')
        else:
            process_enrollment(message)


@bot.message_handler(commands=[*SUPER_ACTIONS[0]])
def handle_kicks(message: Message) -> None:

    super_message = message.text.split(' ')

    if bot.is_superuser:
        bot.kick_chat_member(
            chat_id=super_message[1],
            user_id=super_message[0],
        )


@bot.message_handler(commands=[*SUPER_ACTIONS[1]])
def handle_add(message: Message) -> None:

    super_message = message.text.split(' ')

    if bot.is_superuser:
        bot.send_message(
            super_message[0],
            text=bot.create_chat_invite_link(
                super_message[1]
            )
        )


@bot.message_handler(commands=[*SUPER_ACTIONS[2]])
def clear_data(message: Message) -> None:

    if bot.is_superuser:
        bot.clear_user_data(message.text)


if __name__ == '__main__':
    bot.infinity_polling()
