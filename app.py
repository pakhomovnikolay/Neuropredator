import telebot, wikipediaapi, requests, random, config
from bs4 import BeautifulSoup
from telebot import types
from wikipediaapi import Wikipedia

# Инициализация бота
bot = telebot.TeleBot(config.token)


# Получаем запрашиваемые данные
def get_random_data(url, class_type):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, config.type_parser_html)
        data_list = soup.find_all("div", class_=class_type)
        random_data = random.choice(data_list)
        return random_data.text.strip()
    except Exception:
        return config.exception_get_random_data


# Чистим текст статьи в Wikipedia и ограничиваем его тысячей символов
wiki = Wikipedia("MyProjectName", config.RUS, wikipediaapi.ExtractFormat.WIKI)
def get_wiki(word):
    try:
        reset_need_search()
        page = wiki.page(word)
                
        if page.exists():
            return "Вот что удалось найти:\n" + page.text[:1000]
        else:
            return config.exception_get_wiki

    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception:
        return config.exception_get_wiki

# Получаем анекдот
def get_joke():
    return get_random_data(config.url_joke, config.class_type_joke)


# Получаем интересный факт
def get_fact():
    return get_random_data(config.url_fact, config.class_type_fact)


# Получаем поговорку
def get_proverb():
    return get_random_data(config.url_proverb, config.class_type_proverb)


# Отправляем сообщение об ожидании
def send_message_await(message_chat_id):
    bot_send_message(message_chat_id, config.message_await)


def bot_send_message(chat_id, message):
    try:
        bot.send_message(chat_id, message)
    except Exception:
        bot.send_message(chat_id, config.exception_get_random_data)


def bot_send_message_parse_mode_reply_markup(chat_id, message, parse_mode, reply_markup):
    try:
        bot.send_message(chat_id, message, parse_mode = parse_mode, reply_markup = reply_markup)
    except Exception:
        bot.send_message(chat_id, config.exception_get_random_data)


def bot_send_message_reply_markup(chat_id, message, reply_markup):
    try:
        bot.send_message(chat_id, message, reply_markup = reply_markup)
    except Exception:
        bot.send_message(chat_id, config.exception_get_random_data)


# Обработка команды - Старт
@bot.message_handler(commands=[config.command_start])
def start(message):
    
    # Формируем приветственное сообщение
    second_message = F"<b>{message.from_user.first_name} {message.from_user.last_name}</b>, " + config.message_hello

    # Добавляем две кнопки
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text = config.button_view_blog_text, callback_data = config.button_view_blog_callback))
    markup.add(types.InlineKeyboardButton(text = config.button_talk_text, callback_data = config.button_talk_callback))
    
    # Выдаем сообщение пользоветлю, с возможностью выбора
    bot_send_message_parse_mode_reply_markup(message.chat.id, second_message, config.mode_parse_html, markup)
    reset_need_search()


# Обработка команды - Помощь
@bot.message_handler(commands=[config.command_help])
def start(message):
    bot_send_message(message.chat.id, config.message_help)
    reset_need_search()


# Обработка команды - Перейти в личный блог
@bot.message_handler(commands=[config.command_view])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(config.button_question_send_blog_text, url=config.button_question_send_blog_url))
    bot_send_message_reply_markup(message.chat.id, config.question_send_blog, markup)
    reset_need_search()


# Обработка команды - Рассказать анекдот
@bot.message_handler(commands=[config.command_joke])
def start(message):
    send_message_await(message.chat.id)
    bot_send_message(message.chat.id, get_joke())
    reset_need_search()


# Обработка команды - Рассказать интересный факт
@bot.message_handler(commands=[config.command_fack])
def start(message):
    send_message_await(message.chat.id)
    bot_send_message(message.chat.id, get_fact())
    reset_need_search()


# Обработка команды - Рассказать поговорку
@bot.message_handler(commands=[config.command_proverb])
def start(message):
    send_message_await(message.chat.id)
    bot_send_message(message.chat.id, get_proverb())
    reset_need_search()


# Обработка команды - Поиска значения слова
need_search = True
@bot.message_handler(commands=[config.command_search])
def handle_search(message):
    searchText = message.text.replace("/" + config.command_search, "")
    if searchText == "":
        set_need_search()
        bot_send_message(message.chat.id, config.message_help_search)
    else:
        send_message_await(message.chat.id)
        bot_send_message(message.chat.id, get_wiki(searchText))



# Обработка запросов
@bot.callback_query_handler(func=lambda call:True)
def response(function_call):
    if function_call.message:
        if function_call.data == config.button_view_blog_callback:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(config.button_question_send_blog_text, url = config.button_question_send_blog_url))
            bot_send_message_reply_markup(function_call.message.chat.id, config.question_send_blog, markup)
            bot.answer_callback_query(function_call.id)
        
        elif function_call.data == config.button_talk_callback:
            markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.InlineKeyboardButton(text = config.button_joke_text, callback_data = config.button_joke_callback))
            markup.add(types.InlineKeyboardButton(text = config.button_fact_text, callback_data = config.button_fact_callback))
            markup.add(types.InlineKeyboardButton(text = config.button_proverb_text, callback_data = config.button_proverb_callback))
            markup.add(types.InlineKeyboardButton(text = config.button_word_text, callback_data = config.button_word_callback))
            markup.add(types.InlineKeyboardButton(text = config.button_send_blog_text, callback_data = config.button_send_blog_сallback))
            markup.add(types.InlineKeyboardButton(text = config.button_help_text, callback_data = config.button_help_сallback))
            bot_send_message_reply_markup(function_call.message.chat.id, config.message_talk, markup)
            bot.answer_callback_query(function_call.id)
            
        elif function_call.data == config.button_joke_callback:
            send_message_await(function_call.message.chat.id)
            bot_send_message(function_call.message.chat.id, get_joke())
            bot.answer_callback_query(function_call.id)

        elif function_call.data == config.button_fact_callback:
            send_message_await(function_call.message.chat.id)
            bot_send_message(function_call.message.chat.id, get_fact())
            bot.answer_callback_query(function_call.id)
        
        elif function_call.data == config.button_proverb_callback:
            send_message_await(function_call.message.chat.id)
            bot_send_message(function_call.message.chat.id, get_proverb())
            bot.answer_callback_query(function_call.id)
        
        elif function_call.data == config.button_word_callback:
            set_need_search()
            bot_send_message(function_call.message.chat.id, config.message_help_search)
            bot.answer_callback_query(function_call.id)
        
        elif function_call.data == config.button_help_сallback:
            bot_send_message(function_call.message.chat.id, config.message_help)
            bot.answer_callback_query(function_call.id)


# Обработка текста
@bot.message_handler(content_types=[config.type_content_text])
def handle_text(message):
    
    if message.text.strip() == config.button_joke_text:
        send_message_await(message.chat.id)
        bot_send_message(message.chat.id, get_joke())
        reset_need_search()
    
    elif message.text.strip() == config.button_fact_text:
        send_message_await(message.chat.id)
        bot_send_message(message.chat.id, get_fact())
        reset_need_search()
        
    elif message.text.strip() == config.button_proverb_text:
        send_message_await(message.chat.id)
        bot_send_message(message.chat.id, get_proverb())
        reset_need_search()
    
    elif message.text.strip() == config.button_word_text:
        set_need_search()
        bot.send_message(message.chat.id, config.message_help_search)

    elif message.text.strip() == config.button_send_blog_text:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(config.button_question_send_blog_text, url=config.button_question_send_blog_url))
        bot_send_message_reply_markup(message.chat.id, config.question_send_blog, markup)
        reset_need_search()

    elif message.text.strip() == config.button_help_text:
        bot_send_message(message.chat.id, config.message_help)
        reset_need_search()
        
    else:
        if not need_search:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(config.button_question_send_blog_text, url=config.button_question_send_blog_url))
            bot_send_message_reply_markup(message.chat.id, config.question_send_blog, markup)

        else:
            handle_search(message)


# Сбрасываем флаг запроса поиска значения слова
def reset_need_search():
    global need_search
    need_search = False


# Устанавливаем флаг запроса поиска значения слова
def set_need_search():
    global need_search
    need_search = True


# Запускам бота
bot.infinity_polling()