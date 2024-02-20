from os import getenv
from os.path import exists
from dotenv import load_dotenv
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)
from telegram import Bot, ReplyKeyboardMarkup, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import TelegramError
from datetime import datetime
from info_text import major
from hashlib import sha3_512
from random import choice
from string import ascii_lowercase, ascii_uppercase, digits

load_dotenv()

TOKEN = getenv('token')
MODERATION_CHAT_ID = getenv('moderation_chat_id')
PUBLIC_CHAT_ID = getenv('public_chat_id')
MEMBERS = getenv('members')

SUPERUSERS = tuple(str(getenv('super_users')))
SUPER_COMMANDS = ['kick', 'add', 'delete']

ENCODING = 'utf-8'

UPDATER_INTERVAL = 3600
SALT_SIZE = 16

enroll_in_process = False
waiting_for_admition = False

qustons_copy = dict()
data_container = dict()

qustons_copy['qustons'] = list(major['qustons'])


def any_button_pressed(message: str) -> bool:
    return any(
        list(
            map(
                lambda x: x[0] == message,
                major.keys()
            )
        )
    )


def salt() -> str:
    return ''.join(
        choice(
            ascii_lowercase + ascii_uppercase + digits
        ) for _ in range(SALT_SIZE)
    )


def hasher(data: dict) -> str:
    return '{hp}{sha}'.format(
        hp=major['hash_prefix'],
        sha=sha3_512(f'{data}{salt()}'.encode('utf-8')).hexdigest()
    )


def member(user_id: int) -> bool:
    try:
        bot.get_chat_member(PUBLIC_CHAT_ID, user_id)
    except TelegramError:
        return False
    else:
        return True
    finally:
        return False


def superuser(user_id: int) -> bool:

    return True if user_id in SUPERUSERS else False


def add_to_waiting_queue(bulk_data: tuple) -> None:

    new_admition = f'{bulk_data[0][1]}_apply_queue.txt'

    if not exists(new_admition):
        with open(new_admition, 'w') as new_file:
            new_file.writelines(
                str(
                    bulk_data
                )
            )
            new_file.close()

        with open('waiting_queue.txt', 'w') as main_queue:
            main_queue.writelines(
                str(
                    bulk_data
                )
            )
            main_queue.close()


def process_enrollment(update: Update, context: CallbackContext):

    global enroll_in_process

    if len(qustons_copy['qustons']) == 0:

        waiting_for_admition = True
        enroll_in_process = False

        context.bot.send_message(
            update.message.chat.id, text='Заявка заполнена, ожидайте ответ'
        )

        add_to_waiting_queue(
            (
                ('user_id', update.effective_user.id),
                ('first_name', update.effective_user.name),
                ('username', update.effective_user.username),
                ('data', data_container),
                ('hash', hasher(data_container)),
                ('time', datetime.now()),
            )
        )
    else:
        pointer = qustons_copy['qustons'][0]
        data_container[pointer] = update.message.text.encode(ENCODING)

        context.bot.send_message(update.message.chat.id, text=pointer)

        del qustons_copy['qustons'][0]


def handle_text(update: Update, context: CallbackContext) -> None:

    global enroll_in_process

    current_chat = update.effective_chat
    current_user = update.message.from_user.id
    msg = update.message.text
    bot = context.bot

    if not member(current_user):

        if not enroll_in_process:

            if msg == 'Вступить' and not waiting_for_admition:
                bot.send_message(current_chat.id, text=major['Вступить'][1])
                enroll_in_process = True

            elif msg == 'Вступить' and waiting_for_admition:
                bot.send_message(current_chat.id, text=major['Вступить'][2])

            elif any([x == update.message.text for x in major.keys()]):
                bot.send_message(current_chat.id, major[msg][1])

            else:
                bot.send_message(current_chat.id, text='Неизвестная команда')
        else:
            process_enrollment(update, context)


def ban_member(user_id: int) -> None:

    bot.ban_chat_member(
        chat_id=PUBLIC_CHAT_ID,
        user_id=user_id
    )


def add_member(user_id: int) -> None:

    invite_link = bot.createChatInviteLink(
        chat_id=PUBLIC_CHAT_ID
    )

    bot.send_message(
        chat_id=user_id,
        text=invite_link
    )


def delete_member(user_id: int) -> None:

    with open(str(MEMBERS), 'w') as file:
        for block in file.readlines():
            if block.__contains__(str(user_id)):
                del block

        file.close()


def handle_commands(update: Update, context: CallbackContext) -> None:

    msg = update.message.text
    scalp_message = msg.split()
    current_user = update.effective_chat.id

    if superuser(current_user) and msg in SUPER_COMMANDS:

        globals()[f'{scalp_message[0]}_member'](user_id=scalp_message[1])


def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=major['start'],
        reply_markup=ReplyKeyboardMarkup(
            [[
                'Вступить', 'Документы', 'FAQ', 'Донаты'
            ]]
        )
    )


def main():

    bot = Bot(token=TOKEN)

    updater = Updater(token=TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(
        CommandHandler(SUPER_COMMANDS, handle_commands)
    )
    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_text))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':

    main()
