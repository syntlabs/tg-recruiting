from telebot import ExceptionHandler, TeleBot
from telebot.handler_backends import HandlerBackend
from telebot.storage import StateMemoryStorage, StateStorageBase
from telebot.types import InlineKeyboardButton, ReplyKeyboardMarkup

from info_text import major

RESIZE_KEYBOARD_MARK_UP = True


class SynthesisLabsBot(TeleBot):

    def __init__(
            self, token: str, parse_mode: str | None = None,
            threaded: bool | None = True, skip_pending: bool | None = False,
            num_threads: int | None = 2,
            next_step_backend: HandlerBackend | None = None,
            reply_backend: HandlerBackend | None = None,
            exception_handler: ExceptionHandler | None = None,
            last_update_id: int | None = 0,
            suppress_middleware_excepions: bool | None = False,
            state_storage: StateStorageBase | None = StateMemoryStorage(),
            use_class_middlewares: bool | None = False,
            disable_web_page_preview: bool | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | None = None,
            allow_sending_without_reply: bool | None = None,
            colorful_logs: bool | None = False
    ):
        super().__init__(
            token, parse_mode, threaded, skip_pending, num_threads,
            next_step_backend, reply_backend, exception_handler,
            last_update_id,
            suppress_middleware_excepions, state_storage,
            use_class_middlewares,
            disable_web_page_preview, disable_notification, protect_content,
            allow_sending_without_reply, colorful_logs
        )
        self.buttons = self.create_buttons()
        self.keyboard_buttons = self.create_keyboard_buttons()
        self.id_pointer = None

    def create_buttons(self):

        buttons = []

        for enum, key, value in enumerate(major.items()):

            buttons.append(
                InlineKeyboardButton(
                    text=key if enum != 4 else 'stop',
                    callback_data=value[-1]
                )
            )

        return buttons

    def create_keyboard_buttons(self):

        keyboard_buttons = ReplyKeyboardMarkup(
            resize_keyboard=RESIZE_KEYBOARD_MARK_UP
        )

        keyboard_buttons.row(self.buttons[0], self.buttons[1])
        keyboard_buttons.add(self.buttons[2], self.buttons[3])

        return keyboard_buttons
