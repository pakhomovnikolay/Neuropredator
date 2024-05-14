import telebot, wikipedia, re, requests, random, config
from bs4 import BeautifulSoup
from telebot import *

# Инициализация бота
bot = telebot.TeleBot(config.token)


# Получаем анекдот
def reset_need_search():
    global need_search
    need_search = False


# Получаем запрашиваемые данные
def get_random_data(url, class_type):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        data_list = soup.find_all("div", class_=class_type)
        random_data = random.choice(data_list)
        return random_data.text.strip()
    except Exception:
        return "Не удалось получить данные. Повторите попытку позже"


# Чистим текст статьи в Wikipedia и ограничиваем его тысячей символов
wikipedia.set_lang("ru")
def getwiki(s):
    try:
        global need_search
        need_search = False
        
        ny = wikipedia.page(s)
        # Получаем первую тысячу символов
        wikitext=ny.content[:1000]
        # Разделяем по точкам
        wikimas=wikitext.split('.')
        # Отбрасываем всЕ после последней точки
        wikimas = wikimas[:-1]
        # Создаем пустую переменную для текста
        wikitext2 = ''
        # Проходимся по строкам, где нет знаков «равно» (то есть все, кроме заголовков)
        for x in wikimas:
            if not("==" in x):
                    # Если в строке осталось больше трех символов, добавляем ее к нашей переменной и возвращаем утерянные при разделении строк точки на место
                if(len((x.strip()))>3):
                   wikitext2=wikitext2+x+'.'
            else:
                break
        # Теперь при помощи регулярных выражений убираем разметку
        wikitext2=re.sub("\([^()]*\)", "", wikitext2)
        wikitext2=re.sub("\([^()]*\)", "", wikitext2)
        wikitext2=re.sub("\{[^\{\}]*\}", "", wikitext2)
        # Возвращаем текстовую строку
        return wikitext2
    
    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception:
        return "В энциклопедии нет информации об этом"


# Получаем анекдот
def get_joke():
    return get_random_data(config.url_joke, "anekdot_text")


# Получаем интересный факт
def get_fact():
    return get_random_data(config.url_fact, "story-block story-block_type_text")


# Получаем поговорку
def get_proverb():
    return get_random_data(config.url_proverb, "story")


# Отправляем сообщение об ожидании
def send_message_await(message_chat_id):
    bot.send_message(message_chat_id, config.message_await)


# Обработка команды - Старт
@bot.message_handler(commands=[config.command_start])
def start(message):
    
    # Формируем приветственное сообщение
    second_message = F"<b>{message.from_user.first_name} {message.from_user.last_name}</b>, " + config.hello_message

    # Добавляем две кнопки
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text = config.button_view_blog_text, callback_data = config.button_view_blog_callback))
    markup.add(types.InlineKeyboardButton(text = config.button_talk_text, callback_data = config.button_talk_callback))
    
    # Выдаем сообщение пользоветлю, с возможностью выбора
    bot.send_message(message.chat.id, second_message, parse_mode='html', reply_markup=markup)
    
# Обработка команды - Поиска значения слова
need_search = True
@bot.message_handler(commands=[config.command_search])
def handle_joke(message):
    searchText = message.text.replace("/" + config.command_search, "")
    if searchText == "":
        global need_search
        need_search = True
        bot.send_message(message.chat.id, config.message_help_search)
    else:
        send_message_await(message.chat.id)
        bot.send_message(message.chat.id, getwiki(searchText))
        

# Обработка запросов
@bot.callback_query_handler(func=lambda call:True)
def response(function_call):
    if function_call.message:
        if function_call.data == config.button_view_blog_callback:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(config.button_question_send_blog_text, url = config.button_question_send_blog_url))
            bot.send_message(function_call.message.chat.id, config.question_send_blog, reply_markup = markup)
            bot.answer_callback_query(function_call.id)
        
        elif function_call.data == config.button_talk_callback:
            markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.InlineKeyboardButton(text = config.button_joke_text, callback_data = config.button_joke_callback))
            markup.add(types.InlineKeyboardButton(text = config.button_fact_text, callback_data = config.button_fact_callback))
            markup.add(types.InlineKeyboardButton(text = config.button_proverb_text, callback_data = config.button_proverb_callback))
            markup.add(types.InlineKeyboardButton(text = config.button_word_text, callback_data = config.button_word_callback))
            markup.add(types.InlineKeyboardButton(text = config.button_send_blog_text, callback_data = config.button_send_blog_сallback))
            bot.send_message(function_call.message.chat.id, config.talk_message, reply_markup = markup)
            bot.answer_callback_query(function_call.id)
            
        elif function_call.data == config.button_joke_callback:
            send_message_await(function_call.message.chat.id)
            bot.send_message(function_call.message.chat.id, get_joke())
            bot.answer_callback_query(function_call.id)

        elif function_call.data == config.button_fact_callback:
            send_message_await(function_call.message.chat.id)
            bot.send_message(function_call.message.chat.id, get_fact())
            bot.answer_callback_query(function_call.id)
        
        elif function_call.data == config.button_proverb_callback:
            send_message_await(function_call.message.chat.id)
            bot.send_message(function_call.message.chat.id, get_proverb())
            bot.answer_callback_query(function_call.id)
        
        elif function_call.data == config.button_word_callback:
            global need_search
            need_search = True
            bot.send_message(function_call.message.chat.id, config.message_help_search)
            bot.answer_callback_query(function_call.id)

# Обработка текста
@bot.message_handler(content_types=["text"])
def handle_text(message):
    
    if message.text.strip() == config.button_joke_text:
        send_message_await(message.chat.id)
        bot.send_message(message.chat.id, get_joke())
        reset_need_search()
    
    elif message.text.strip() == config.button_fact_text:
        send_message_await(message.chat.id)
        bot.send_message(message.chat.id, get_fact())
        reset_need_search()
        
    elif message.text.strip() == config.button_proverb_text:
        send_message_await(message.chat.id)
        bot.send_message(message.chat.id, get_proverb())
        reset_need_search()
    
    elif message.text.strip() == config.button_word_text:
        global need_search
        need_search = True
        bot.send_message(message.chat.id, config.message_help_search)
        
    elif message.text.strip() == config.button_send_blog_text:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(config.button_question_send_blog_text, url=config.button_question_send_blog_url))
        bot.send_message(message.chat.id, config.question_send_blog, reply_markup=markup)
        reset_need_search()
    
    else:
        if not need_search:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(config.button_question_send_blog_text, url=config.button_question_send_blog_url))
            bot.send_message(message.chat.id, config.question_send_blog, reply_markup=markup)
        
        else:
            handle_joke(message)
            

# Запускам бота
bot.infinity_polling()