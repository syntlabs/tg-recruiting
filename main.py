import telebot as tlb
from hashlib import sha3_512

bot_token = '' #надо брать из .env
test_token = '' #надо брать из .env
rules_txt = 'Пожалуйста, ознакомьтесь с нашей документацией'
FAQ_text = 'FAQ находится в работе. Пока можете ознакомиться с нашим сайтом: \nsyntlabs.com'
crypto_donats = 'В настоящее время пожертвования принимаются только в TON.\n\nTON: `syntlabs.ton`'
support_text = 'Вы можете поддержать движение, отправив криптовалюту на один из нижеперечисленных адресов.'
test_chat_id = 0 #надо брать из .env
group_chat_id = 0 #надо брать из .env
main_channel_id = 0 #надо брать из .env
bot = tlb.TeleBot(bot_token)

start_text ='Привет! Я бот для трудоустройства в Synthesis Labs.\n\nБлагодаря мне вы можете подать заявку на соискание должности в компании, сделать пожертвование, а в будещем я обрету еще больше функций.\n\nВыберите дальнейшее действие:'

success_enroll = 'Ваша заявка принята на проверку. Пожалуйста ожидайте, с Вами свяжутся.'
enroll_text = 'Вступить'
rules_text = 'Документы'
donats_text = 'Пожертвования'
faq = "FAQ"

hash_prefix = 'SYNTx'

content_types = ['id: ','имя: ','юзернейм: ', 'данные: ','хеш: ']
enroll_form_text = 'Для рассмотрения вашей заявки заполните анкету.\n\nВы можете в любой момент прекратить заполнение анкеты, написав мне «stop» (без кавычек).\n\nДля начала, укажите свои ФИО'
content_qustons = [
    'ФИО',
    'Город',
    'Дата рождения',
    'Опишите свои навыки и умения',
    'Имеется ли у вас опыт блокчейн разработки',
    'Имеется ли у вас опыт в сфере дизайна сайтов и приложений',
    'Укажите свои социальные сети, если таковые имеются',
    'Откуда узнали о проекте?'
]


first = tlb.types.InlineKeyboardButton(text=enroll_text, callback_data='join')
second = tlb.types.InlineKeyboardButton(text=rules_text, callback_data='docs')
third = tlb.types.InlineKeyboardButton(text=donats_text, callback_data='docs')
fourth = tlb.types.InlineKeyboardButton(text=faq, callback_data='docs')
five = tlb.types.InlineKeyboardButton(text='stop', callback_data='stop')


keyboard_buttons = tlb.types.ReplyKeyboardMarkup(resize_keyboard = True)
keyboard_buttons.row(first, second)
keyboard_buttons.add(third, fourth)


@bot.message_handler(commands=['start'])

def start (message, res=False):

  bot.send_message(message.chat.id, start_text, reply_markup=keyboard_buttons)

@bot.message_handler(content_types=["text"])

def handle_text (message) :

  current_chat = message.chat.id

  if message.text == enroll_text:

    if not member(group_chat_id, message.from_user.id):
        bot.send_message(current_chat, enroll_form_text)
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(current_chat, enroll_form_text)
        bot.register_next_step_handler(message, get_name)
  elif message.text == rules_text:
      bot.send_message(current_chat, 'Документация по проекту будет опубликована позднее.')

  elif message.text == donats_text:
    bot.send_message(current_chat, support_text)
    bot.send_message(current_chat, crypto_donats, parse_mode="Markdown")
  elif message.text == faq:
    bot.send_message(current_chat, FAQ_text)
  elif message.text == 'AllowS1':
    bot.send_message(current_chat, 'Введите ID')
    bot.register_next_step_handler(message, allowStepOne)
  elif message.text == 'AllowS2':
    bot.send_message(current_chat, 'Введите ID')
    bot.register_next_step_handler(message, allowStepTwo)
  elif message.text == 'DenyS1':
    bot.send_message(current_chat, 'Введите ID')
    bot.register_next_step_handler(message, denyS1)
  else:
    bot.send_message(current_chat, 'Неизвестная комманда')

def get_name(message):
    if message.text == 'stop':
        bot.send_message(message.from_user.id, 'Заполнение анкеты приостановлено. Вы сможете продолжить позднее.')
    elif message.text == enroll_text:
        bot.send_message(message.from_user.id, 'Вы уже заполняете анкету. Пожалуйста, укажите свои ФИО.')
        bot.register_next_step_handler(message, get_name)
    elif message.text == rules_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свои ФИО.')
        bot.register_next_step_handler(message, get_name)
    elif message.text == donats_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свои ФИО.')
        bot.register_next_step_handler(message, get_name)
    elif message.text == faq:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свои ФИО.')
        bot.register_next_step_handler(message, get_name)
    else:
        global name
        name = message.text
        bot.send_message(message.from_user.id, 'Из какого ты города?')
        bot.register_next_step_handler(message, get_city) 

def get_city(message):
    if message.text == 'stop':
        bot.send_message(message.from_user.id, 'Заполнение анкеты приостановлено. Вы сможете продолжить позднее.')
    elif message.text == enroll_text:
        bot.send_message(message.from_user.id, 'Вы уже заполняете анкету. Пожалуйста, укажите свой город.')
        bot.register_next_step_handler(message, get_city)
    elif message.text == rules_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свой город.')
        bot.register_next_step_handler(message, get_city)
    elif message.text == donats_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свой город.')
        bot.register_next_step_handler(message, get_city)
    elif message.text == faq:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свой город.')
        bot.register_next_step_handler(message, get_city)
    else:
        global city
        city = message.text
        bot.send_message(message.from_user.id, 'Дата рождения')
        bot.register_next_step_handler(message, get_age)

def get_age(message): 
    if message.text == 'stop':
        bot.send_message(message.from_user.id, 'Заполнение анкеты приостановлено. Вы сможете продолжить позднее.')
    elif message.text == enroll_text:
        bot.send_message(message.from_user.id, 'Вы уже заполняете анкету. Пожалуйста, укажите свою дату рождения.')
        bot.register_next_step_handler(message, get_age)
    elif message.text == rules_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свою дату рождения.')
        bot.register_next_step_handler(message, get_age)
    elif message.text == donats_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свою дату рождения.')
        bot.register_next_step_handler(message, get_age)
    elif message.text == faq:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свою дату рождения.')
        bot.register_next_step_handler(message, get_age)
    else:
        global age
        age = message.text
        bot.send_message(message.from_user.id, 'Опишите свои навыки и умения')
        bot.register_next_step_handler(message, get_skills)  
  

def get_skills(message):
    if message.text == 'stop':
        bot.send_message(message.from_user.id, 'Заполнение анкеты приостановлено. Вы сможете продолжить позднее.')
    elif message.text == enroll_text:
        bot.send_message(message.from_user.id, 'Вы уже заполняете анкету. Пожалуйста, укажите свои навыки и умения.')
        bot.register_next_step_handler(message, get_skills)
    elif message.text == rules_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свои навыки и умения.')
        bot.register_next_step_handler(message, get_skills)
    elif message.text == donats_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свои навыки и умения.')
        bot.register_next_step_handler(message, get_skills)
    elif message.text == faq:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свои навыки и умения.')
        bot.register_next_step_handler(message, get_skills)
    else:
        global skills
        skills = message.text
        bot.send_message(message.from_user.id, 'Имеется ли у вас опыт блокчейн-разработки?')
        bot.register_next_step_handler(message, get_politics)

def get_politics(message):
    if message.text == 'stop':
        bot.send_message(message.from_user.id, 'Заполнение анкеты приостановлено. Вы сможете продолжить позднее.')
    elif message.text == enroll_text:
        bot.send_message(message.from_user.id, 'Вы уже заполняете анкету. Пожалуйста, укажите имеется ли у вас опыт блокчейн-разработки.')
        bot.register_next_step_handler(message, get_politics)
    elif message.text == rules_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите имеется ли у вас опыт блокчейн-разработки.')
        bot.register_next_step_handler(message, get_politics)
    elif message.text == donats_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите имеется ли у вас опыт блокчейн-разработки.')
        bot.register_next_step_handler(message, get_politics)
    elif message.text == faq:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите имеется ли у вас опыт блокчейн-разработки.')
        bot.register_next_step_handler(message, get_politics)
    else:
        global politics
        politics = message.text
        bot.send_message(message.from_user.id, 'Имеется ли у вас опыт в сфере дизайна сайтов и приложений?')
        bot.register_next_step_handler(message, get_nap)

def get_nap(message):
    if message.text == 'stop':
        bot.send_message(message.from_user.id, 'Заполнение анкеты приостановлено. Вы сможете продолжить позднее.')
    elif message.text == enroll_text:
        bot.send_message(message.from_user.id, 'Вы уже заполняете анкету. Пожалуйста, укажите имеется ли у вас опыт в сфере дизайна сайтов и приложений.')
        bot.register_next_step_handler(message, get_nap)
    elif message.text == rules_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите имеется ли у вас опыт в сфере дизайна сайтов и приложений.')
        bot.register_next_step_handler(message, get_nap)
    elif message.text == donats_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите имеется ли у вас опыт в сфере дизайна сайтов и приложений.')
        bot.register_next_step_handler(message, get_nap)
    elif message.text == faq:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите имеется ли у вас опыт в сфере дизайна сайтов и приложений.')
        bot.register_next_step_handler(message, get_nap)
    else:
        global nap
        nap = message.text
        bot.send_message(message.from_user.id, 'Укажите свои социальные сети, если таковые имеются')
        bot.register_next_step_handler(message, get_socials)

def get_socials(message):
    if message.text == 'stop':
        bot.send_message(message.from_user.id, 'Заполнение анкеты приостановлено. Вы сможете продолжить позднее.')
    elif message.text == enroll_text:
        bot.send_message(message.from_user.id, 'Вы уже заполняете анкету. Пожалуйста, укажите свои социальные сети, если таковые имеются.')
        bot.register_next_step_handler(message, get_socials)
    elif message.text == rules_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свои социальные сети, если таковые имеются.')
        bot.register_next_step_handler(message, get_socials)
    elif message.text == donats_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свои социальные сети, если таковые имеются.')
        bot.register_next_step_handler(message, get_socials)
    elif message.text == faq:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nПожалуйста, укажите свои социальные сети, если таковые имеются.')
        bot.register_next_step_handler(message, get_socials)
    else:
        global socials
        socials = message.text
        bot.send_message(message.from_user.id, 'Откуда узнали о нашем проекте?')
        bot.register_next_step_handler(message, get_rules)


def get_rules(message):
    if message.text == 'stop':
        bot.send_message(message.from_user.id, 'Заполнение анкеты приостановлено. Вы сможете продолжить позднее.')
    elif message.text == enroll_text:
        bot.send_message(message.from_user.id, 'Вы уже заполняете анкету. Откуда узнали о нашем проекте?')
        bot.register_next_step_handler(message, get_rules)
    elif message.text == rules_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nОткуда узнали о нашем проекте?')
        bot.register_next_step_handler(message, get_rules)
    elif message.text == donats_text:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nОткуда узнали о нашем проекте?')
        bot.register_next_step_handler(message, get_rules)
    elif message.text == faq:
        bot.send_message(message.from_user.id, 'Данная команда временно недоступна — вы заполняете анкету.\nВы можете продолжить заполнение анкеты, либо прервать его отправив в чат «stop» (без кавычек).\n\nОткуда узнали о нашем проекте?')
        bot.register_next_step_handler(message, get_rules)
    else:
        global rules
        rules = message.text
        data = 'ФИО: ' + name + '\nГород: ' + city + '\nДата рождения: ' + age + '\nНавыки и умения: ' + skills + '\nОпыт блокчейн разработки: ' + politics + '\nОпыт дизайна: ' + nap +'\nСоциальные сети: ' + socials + '\nОткуда узнал о нас: ' + rules
        hash = hash_prefix + sha3_512(data.encode('utf-8')).hexdigest()
        bot.send_message(
            test_chat_id, 
            [str(message.chat.id) + '\n' + str(message.from_user.first_name) + '\n' + str(message.from_user.username) + '\n' + str(data) + '\n' + str(hash)])
        bot.send_message(message.from_user.id, success_enroll)

def exit(message):
    bot.send_message(message.from_user.id, 'Заполнение анкеты приостановлено. Вы сможете продолжить позднее.')

def allowStepOne(message):
    if message.from_user.id == 900659397:
        global id
        id = message.text
        if message.text == 'me':
            id = message.from_user.id
        bot.send_message(id, 'Доброго времени суток! По итогам рассмотрения вашей заявки Synthesis Labs приглашает вас на непродолжительную беседу. В ближайшее время с вами свяжется наш предствитель и вы сможете выбрать удобное для вас время.')
        bot.send_message(test_chat_id, 'Done.')
    elif message.from_user.id == 5116022329:
        id = message.text
        if message.text == 'me':
            id = message.from_user.id
        bot.send_message(id, 'Доброго времени суток! По итогам рассмотрения вашей заявки Synthesis Labs приглашает вас на непродолжительную беседу. В ближайшее время с вами свяжется наш предствитель и вы сможете выбрать удобное для вас время.')
        bot.send_message(test_chat_id, 'Done.')
    else:
        bot.send_message(message.from_user.id, 'У вас недостаточно прав!')

def allowStepTwo(message):
    if message.from_user.id == 900659397:
        global id
        id = message.text
        if message.text == 'me':
            id = message.from_user.id
        bot.send_message(id, 'Доброго времени суток! По итогам рассмотрения вашей заявки Synthesis Labs принял решение о вашем принятии.\n\nРабочий чат:https://t.me/+TM3DSK4bLqg1OTgy')
        bot.send_message(test_chat_id, 'Done.')
    elif message.from_user.id == 5116022329:
        id = message.text
        if message.text == 'me':
            id = message.from_user.id
        bot.send_message(id, 'Доброго времени суток! По итогам рассмотрения вашей заявки Synthesis Labs принял решение о вашем принятии.\n\nРабочий чат: https://t.me/+TM3DSK4bLqg1OTgy')
        bot.send_message(test_chat_id, 'Done.')
    else:
        bot.send_message(message.from_user.id, 'У вас недостаточно прав!')

def denyS1(message):
    if message.from_user.id == 900659397:
        global id
        id = message.text
        if message.text == 'me':
            id = message.from_user.id
        bot.send_message(id, 'Доброго времени суток! По итогам рассмотрения вашей заявки Synthesis Labs принял решение об отказе в приеме.')
        bot.send_message(test_chat_id, 'Done.')
    elif message.from_user.id == 5116022329:
        id = message.text
        if message.text == 'me':
            id = message.from_user.id
        bot.send_message(id, 'Доброго времени суток! По итогам рассмотрения вашей заявки Synthesis Labs принял решение об отказе в приеме.')
        bot.send_message(test_chat_id, 'Done.')
    else:
        bot.send_message(message.from_user.id, 'У вас недостаточно прав!')

def member(chat_id, user_id):
      try:
          bot.get_chat_member(chat_id, user_id)
          return True
      except tlb.apihelper.ApiTelegramException as error:
          if error.result_json['description'] == 'Bad Request: user not found':
              return False

bot.polling(none_stop=True, interval=0)
 
