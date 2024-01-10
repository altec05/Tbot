import datetime

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import telebot
import random
import atexit
import re

import config
import db_funcs
import db_funcs as db_f
import keyboards

commands = {
    'help': 'Вызов справки о возможностях бота',
    'start': 'Запуск работы бота',
    'main_menu': 'Вызов главного меню',
    'anekdot': 'Получить анекдот'
}

# user_id : [anekdot_id]
user_views_dict = {

}

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start', 'main_menu'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Привет, Я АнексоБот, чем займемся?', reply_markup=keyboards.main_menu)


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith('/get_'):
        get_anekdot_show_callback(query)
    elif data.startswith('/add_'):
        add_anekdot_callback(query)
    else:
        bot.send_message(query.message.chat.id, '❌ Я ещё этого не умею!')


def get_anekdot_show_callback(query):
    bot.answer_callback_query(query.id)
    if query.data[5:] == 'anekdot':
        send_anekdot_result(query.message)


def add_anekdot_callback(query):
    bot.answer_callback_query(query.id)
    if query.data[5:] == 'anekdot':
        show_dialog_title(query)


def show_dialog_title(query):
    question = bot.send_message(query.message.chat.id, f'Укажите заголовок для анекдота или "/exit":',
                                parse_mode='HTML')
    bot.register_next_step_handler(question, get_title)


def get_title(message):
    if message.text.strip() != '' and message.text.strip() != '/exit':
        title = message.text.strip()
        show_dialog_body(message, title)
    elif message.text.strip() == '/exit':
        bot.send_message(message.chat.id, f'❌ Отмена.')
    else:
        bot.send_message(message.chat.id, f'❌ Заголовок не должен быть пустым.')
        if message.text.strip() == '' or message.text.strip() != '/exit':
            question = bot.send_message(message.message.chat.id, f'Укажите заголовок для анекдота или "/exit":',
                                        parse_mode='HTML')
            bot.register_next_step_handler(question, get_title)


def show_dialog_body(message, title):
    question = bot.send_message(message.chat.id, f'Введите анекдот или "/exit":', parse_mode='HTML')
    bot.register_next_step_handler(question, get_body, title)


def get_body(message, title):
    if message.text.strip() != '' and message.text.strip() != '/exit':
        title = title.replace('/', '')
        body = message.text.strip().replace('/', '')
        add_anekdot(message, body, title)
    elif message.text.strip() == '/exit':
        bot.send_message(message.chat.id, f'❌ Отмена.')
    else:
        bot.send_message(message.chat.id, f'❌ Текст анекдота не должен быть пустым.')
        if message.text.strip() == '' or message.text.strip() != '/exit':
            question = bot.send_message(message.message.chat.id, f'Введите анекдот или "/exit":', parse_mode='HTML')
            bot.register_next_step_handler(question, get_title)


def add_anekdot(message, body, title):
    if title != '' and body != '':
        if db_funcs.add_anekdot([title, body, True]):
            bot.send_message(message.chat.id, f'✅ Анекдот "{title}" добавлен!')
        else:
            bot.send_message(message.chat.id, f'❌ Анекдот "{title}" не добавлен.')
    else:
        bot.send_message(message.chat.id, f'❌ Анекдот "{title}" не добавлен, указаны пустые строки при заполнении.')


def send_anekdot_result(message):
    bot.send_chat_action(message.chat.id, 'typing')
    result = get_one_anekdot(message)
    if result:
        if result != True:
            bot.send_message(message.chat.id, f'{result[1]}\n{result[2]}', parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, f'❌ Анекдотов нет.')


def get_one_anekdot(message):
    anekdots_list = db_f.get_anekdots_list()
    anekdots_views_list = get_views_list_from_dict(message.from_user.id)
    # anekdots_views_list = db_f.get_anekdots_views_list(message.from_user.id)
    if anekdots_views_list != False and len(anekdots_list) > 0:
        temp = []
        for item in anekdots_list:
            temp.append((item[0], item[1], item[2]))
        anekdot = random.choice(temp)
        if not any(str(anekdot[0]) in sublist for sublist in anekdots_views_list):
            anekdots_views_list.append(anekdot[0])
            add_view_in_dict(message.from_user.id, int(anekdot[0]))
            # db_f.add_views_anekdot([message.from_user.id, anekdots_views_list])
            return anekdot
        else:
            counter_try = 0
            while any(str(anekdot[0]) in sublist for sublist in anekdots_views_list) and counter_try <= len(anekdots_list):
                anekdot = random.choice(temp)
                counter_try += 1
            if not any(str(anekdot[0]) in sublist for sublist in anekdots_views_list):
                anekdots_views_list.append(anekdot[0])
                add_view_in_dict(message.from_user.id, int(anekdot[0]))
                # db_f.add_views_anekdot(anekdots_views_list)
                return anekdot
            else:
                if update_bd_from_dict():
                    print('База данных заполнена и обновлена после просмотра всех ан-ов!')
                else:
                    print('База данных не заполнена после просмотра всех ан-ов!')
                if clear_views_dict(message.from_user.id):
                # if db_f.clear_anekdot_views_for_user(message.from_user.id):
                    bot.send_message(message.chat.id, f'❌ Анекдоты закончились, будут повторяться.')
                    return True
                else:
                    return False
    elif len(anekdots_list) == 0:
        return False
    else:
        # anekdots_views_list = [message.from_user.id, []]
        temp = []
        for item in anekdots_list:
            temp.append((item[0], item[1], item[2]))
        anekdot = random.choice(temp)
        # anekdots_views_list[1].append(anekdot[0])
        if add_view_in_dict(message.from_user.id, int(anekdot[0])):
            return anekdot
        else:
            return False
        # db_f.add_views_anekdot(anekdots_views_list)


# Заносим в словарь просмотр
def add_view_in_dict(user_id: int, view):
    if user_id != '':
        views = user_views_dict.get(user_id)
        if views is not None:
            if len(list(views)) == 0:
                user_views_dict[user_id] = [view]
            else:
                views.append(view)
                user_views_dict[user_id] = views
            return True
        else:
            user_views_dict[user_id] = [view]
            return True
    else:
        return False


# Получаем просмотры из словаря
def get_views_list_from_dict(user_id):
    if user_id != '':
        views = user_views_dict.get(user_id)
        if views is not None:
        # views = list(user_views_dict[user_id])
            str_list = []
            for i in views:
                str_list.append(str(i))
            return str_list
        else:
            return False
    else:
        return False


# Очищаем для юзера список просмотренных анекдотов
def clear_views_dict(user_id):
    if user_id != '':
        user_views_dict[user_id] = ['']
        return True
    else:
        return False


# Заполняем словарь в БД
def update_bd_from_dict():
    if len(user_views_dict) > 0:
        send_data = []
        for key in user_views_dict.keys():
            ids = list(user_views_dict[key])
            temp_str = ''
            for i in ids:
                temp_str += str(i) + ' '
            send_data.append([key, temp_str])
        db_funcs.add_views_to_anekdots(send_data)
        return True
    else:
        return False


# регистрируем функцию goodbye() в качестве функции завершения программы
@atexit.register
def goodbye(message=None):
    # отправляем сообщение о том, что бот выключен и словарь записан в БД
    if update_bd_from_dict():
        print('База данных заполнена и обновлена!')
    else:
        print('База данных не заполнена!')

    if message is not None:
        bot.send_message(message.chat.id, f'❌ Работа бота завершена.')


# Завершаем работу бота по команде
@bot.message_handler(commands=['stop_bot'])
def stop_command(message):
  goodbye(message)
  bot.stop_polling()
  print("Бот остановлен")


# Получаем просмотры из БД и заполняем словарь
def fill_views_dict():
    aneks_views = db_f.get_views_from_bd()
    for item in aneks_views:
        ids = item[1].strip().split(' ')
        # for id in item[1]:
        #     ids.append(int(id))
        user_views_dict[item[0]] = ids
    return True


# Очищаем список сообщений
@bot.message_handler(commands=['clear_msgs'])
def clear_msgs(message):
    stop = message.message_id
    for i in range(0, stop):
        try:
            bot.delete_message(message.chat.id, i)
        except:
            pass


if __name__ == '__main__':
    print('Бот запущен...')
    if not db_f.check_db_silent():
        result = db_f.create_db()
        print(f'{result[0]}, {result[1]}')

    if fill_views_dict():
        print('Словарь заполнен просмотрами из БД')

    if db_f.check_db_silent():
        bot.infinity_polling()
    else:
        print('БД не найдена, бот не запущен!')
