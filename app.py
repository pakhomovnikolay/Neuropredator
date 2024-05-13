import telebot, wikipedia, re, requests, random
from bs4 import BeautifulSoup
#from EdgeGPT import Chatbot
from telebot import *

searchTag = ""
need_search = False
bot = telebot.TeleBot('6719735019:AAGCG74MlehHuIWp4Y9C9IEDoFQ9LQURu7A')
urlJoke = 'http://anekdotme.ru/random'
urlFact = 'https://pikabu.ru/community/interesting'
urlProverb = 'https://wisdomlib.ru/catalog/poslovicy-i-pogovorki'

'''
async def bing_chat(prompt):
    # Функция получения ответа от BingAI с использованием cookies.
    bing_ai = await Chatbot.create(cookie_path='./data/cookies.json')
    response_dict = await bing_ai.ask(prompt)
    return response_dict['item']['messages'][1]['text'].replace("[^\\d^]", "")

'''

# Получаем анекдот
def get_random_joke():
    response = requests.get(urlJoke)
    soup = BeautifulSoup(response.text, 'html.parser')

    data_list = soup.find_all('div', class_='anekdot_text')
    random_data = random.choice(data_list)

    return random_data.text.strip()

# Получаем интересный факт
def get_random_fact():
    response = requests.get(urlFact)
    soup = BeautifulSoup(response.text, 'html.parser')

    data_list = soup.find_all('div', class_='story-block story-block_type_text')
    random_data = random.choice(data_list)

    return random_data.text.strip()

# Получаем поговорку
def get_random_proverb():
    response = requests.get(urlProverb)
    soup = BeautifulSoup(response.text, 'html.parser')

    data_list = soup.find_all('div', class_='story')
    random_data = random.choice(data_list)

    return random_data.text.strip()

@bot.message_handler(commands=['start'])
def start(message):
    # Добавляем две кнопки
    msg = f"""<b>{message.from_user.first_name} {message.from_user.last_name}</b>, привет!\nЭто виртуальный помощник Пахомовой Екатерины Эдуардовны\n
            Если тебе интересна тематика материнства и все, что связанно с развлечением, развитием и воспитианием детей, \n
            я могу перенести тебя на её личный блог.\nИли можем просто поболтать"""
    markup = types.InlineKeyboardMarkup()
    button_fact = types.InlineKeyboardButton(text = "Хочу узнать больше про блог", callback_data='ViewBlog')
    button_talk= types.InlineKeyboardButton(text = "Нет, давай лучше поболтаем", callback_data='Talk')
    markup.add(button_fact)
    markup.add(button_talk)
    bot.send_message(message.chat.id, msg, parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda call:True)
def response(function_call):
    if function_call.message:
        if function_call.data == "ViewBlog":
            second_mess = "Перейти на страницу личного блога Екатерины Эдуардовны?"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Перейти на страницу", url="https://t.me/KaterinaPakhomovaa"))
            bot.send_message(function_call.message.chat.id, second_mess, reply_markup=markup)
            bot.answer_callback_query(function_call.id)
        
        elif function_call.data == "Talk":
            second_mess = "Я могу рассказать тебе анекдот, могут рассказать интересный факт, могу рассказать поговорку, могу рассказать значение любого слова, а могу просто поболтать с тобой"
            markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.InlineKeyboardButton(text = "Расскажи мне анекдот", callback_data='Joke'))
            markup.add(types.InlineKeyboardButton(text = "Расскажи мне интересный факт", callback_data='Fact'))
            markup.add(types.InlineKeyboardButton(text = "Расскажи мне поговорку", callback_data='Proverb'))
            markup.add(types.InlineKeyboardButton(text = "Хочу унать значение слова", callback_data='Word'))
            markup.add(types.InlineKeyboardButton(text = "Давай просто поболтаем", callback_data='Talking'))

            bot.send_message(function_call.message.chat.id, second_mess, reply_markup=markup)
            bot.answer_callback_query(function_call.id)
        
        elif function_call.data == "Joke":
            second_mess = "Виду поиск анекдота. Минутку, пожалуйста"
            bot.send_message(function_call.message.chat.id, second_mess)
            
            second_mess = get_random_joke()
            bot.send_message(function_call.message.chat.id, second_mess)
            
            bot.answer_callback_query(function_call.id)
        
        elif function_call.data == "Fact":
            second_mess = "Виду поиск интересных фактов. Минутку, пожалуйста"
            bot.send_message(function_call.message.chat.id, second_mess)
            
            second_mess = get_random_fact()
            bot.send_message(function_call.message.chat.id, second_mess)
            
            bot.answer_callback_query(function_call.id)
            
        elif function_call.data == "Proverb":
            second_mess = "Виду поиск поговорок. Минутку, пожалуйста"
            bot.send_message(function_call.message.chat.id, second_mess)
            
            second_mess = get_random_proverb()
            bot.send_message(function_call.message.chat.id, second_mess)
            
            bot.answer_callback_query(function_call.id)

        elif function_call.data == "Word":
            second_mess = "Отправь мне любое слово, и я расскажу тебе его значение. Для этого введи команду /Search, а после неё напишие искомое слово"
            bot.send_message(function_call.message.chat.id, second_mess)
            bot.answer_callback_query(function_call.id)

# Получение сообщений от юзера
@bot.message_handler(commands=['Search'])
def handle_joke(message):
    searchText = message.text.replace("/Search", "")
    if searchText != "":
        bot.send_message(message.chat.id, "Пошел искать значение слова. Минутку, пожалуйста")
        bot.send_message(message.chat.id, getwiki(message.text.replace("/Search", "")))

@bot.message_handler(content_types=["text"])
def handle_text(message):
        
    if message.text.strip() == "Расскажи мне анекдот":
        second_mess = "Виду поиск анекдота. Минутку, пожалуйста"
        bot.send_message(message.chat.id, second_mess)
        
        second_mess = get_random_joke()
        bot.send_message(message.chat.id, second_mess)
    
    elif message.text.strip() == "Расскажи мне интересный факт":
        second_mess = "Виду поиск интересных фактов. Минутку, пожалуйста"
        bot.send_message(message.chat.id, second_mess)
        
        second_mess = get_random_fact()
        bot.send_message(message.chat.id, second_mess)
        
    elif message.text.strip() == "Расскажи мне поговорку":
        second_mess = "Виду поиск поговорок. Минутку, пожалуйста"
        bot.send_message(message.chat.id, second_mess)
        
        second_mess = get_random_proverb()
        bot.send_message(message.chat.id, second_mess)

    elif message.text.strip() == "Хочу унать значение слова":
        second_mess = "Отправь мне любое слово, и я расскажу тебе его значение. Для этого введи команду /Search, а после неё напишие искомое слово (в одной строке)"
        bot.send_message(message.chat.id, second_mess)
        global need_search
        need_search = True

    elif message.text.strip() == "Давай просто поболтаем":
        second_mess = "Перейти на страницу личного блога Екатерины Эдуардовны?"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Перейти на страницу", url="https://t.me/KaterinaPakhomovaa"))
        bot.send_message(message.chat.id, second_mess, reply_markup=markup)
        
    else:
        if need_search == False:
            second_mess = "Перейти на страницу личного блога Екатерины Эдуардовны?"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Перейти на страницу", url="https://t.me/KaterinaPakhomovaa"))
            bot.send_message(message.chat.id, second_mess, reply_markup=markup)
        
        else:
            bot.send_message(message.chat.id, "Пошел искать значение слова. Минутку, пожалуйста")
            bot.send_message(message.chat.id, getwiki(message.text))

# Устанавливаем русский язык в Wikipedia
wikipedia.set_lang("ru")

# Чистим текст статьи в Wikipedia и ограничиваем его тысячей символов
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
            if not('==' in x):
                    # Если в строке осталось больше трех символов, добавляем ее к нашей переменной и возвращаем утерянные при разделении строк точки на место
                if(len((x.strip()))>3):
                   wikitext2=wikitext2+x+'.'
            else:
                break
        # Теперь при помощи регулярных выражений убираем разметку
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\([^()]*\)', '', wikitext2)
        wikitext2=re.sub('\{[^\{\}]*\}', '', wikitext2)
        # Возвращаем текстовую строку
        return wikitext2
    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception as e:
        return 'В энциклопедии нет информации об этом'

# =======================================================================================================
bot.infinity_polling()