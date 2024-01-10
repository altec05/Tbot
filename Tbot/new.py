import datetime

from telebot.async_telebot import AsyncTeleBot
from telebot.types import  InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import telebot
import re

import db_funcs
import db_funcs as db_f

bot = AsyncTeleBot('6150292237:AAEnbt96pgMpagHg8uQRWCZEgp4-PRHHUB0')

commands = {
    'help' : 'Вызов справки о возможностях бота',
    'start' : 'Запуск работы бота',
    'main_menu': 'Вызов главного меню',
    'new_film': 'Добавить новый фильм',
    'edit_film': 'Изменить фильм',
    'del_film': 'Удалить фильм',
    'rate_film': 'Оценить просмотренный фильм',
}


# Кнопки главного меню
def get_main_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Список фильмов', callback_data='/show_films'),
               InlineKeyboardButton('Список категорий', callback_data='/show_categories'),
               InlineKeyboardButton('Добавить категорию', callback_data='/add_category'),
               InlineKeyboardButton('Оценить фильм', callback_data='/rate-film'),
               InlineKeyboardButton('Добавить фильм', callback_data='/add_film'),)
    return markup


def get_categories_list_str():
    categories_str = ''
    for i in db_funcs.get_categories_list():
        categories_str += f'{i[0]}\n'
    return categories_str


def get_films_list_str():
    films_str = ''
    for i in db_funcs.get_films_list():
        films_str += f'{i[0]}. Фильм {i[1]} ({i[2]})\nКатегория:{i[3]}\nРейтинг КП: {i[4]}\nОписание: {i[6]}.\nПросмотрено: {i[7]}, моя оценка - {i[8]}.'
    return films_str


@bot.message_handler(commands=['start', 'main_menu'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, 'Привет, Я ФильмерБот, чем займемся?', reply_markup=get_main_markup())


@bot.message_handler(commands=['help'])
async def send_welcome(message):
    help_str = ''
    for key in commands.keys():
        help_str += f'/{key}: {commands[key]}.\n'

    await bot.send_message(message.chat.id, f'Привет, Я ТестБот в разработке!\nИ вот что я умею:\n\n{help_str}')


def get_timestamp(now):
    return datetime.datetime.timestamp(now)


def get_date(tmstmp):
    return datetime.datetime.fromtimestamp((tmstmp).date)


# Получить названия категорий
def get_categories():
    categories = []
    for i in db_funcs.get_categories_list():
        categories.append(i[0])
    return categories


# Получить список фильмов
def get_films():
    films = []
    for i in db_funcs.get_films_list():
        films.append((i[0], i[1], i[2], i[3], i[4]))
    return films


@bot.callback_query_handler(func=lambda call: True)
async def get_callback(query):
    data = query.data
    if data.startswith('/show_'):
        await bot.answer_callback_query(query.id)
        await send_show_result(query.message, query.data[6:])


async def show_items(message, show_data):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    if show_data[0][0] == 'films':
        films_list = show_data[1:]
        if len(films_list) > 0:
            for film in films_list:
                keyboard.add(InlineKeyboardButton(f'{film[1]} ({film[2]})\n, категория - {film[3]}\n, оценка - {film[4]}', callback_data=f'/edit_film:{film[0]}'))
            await bot.send_message(message.chat.id, '<b>Фильмы</b>', reply_markup=keyboard, parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, '❌ Список фильмов пуст!')
    elif show_data[0][0] == 'categories':
        categories_list = show_data[1:]
        if len(categories_list) > 0:
            for cat in categories_list:
                keyboard.add(InlineKeyboardButton(f'{cat[1]}', callback_data=f'/edit_category:{cat[0]}'), )
            await bot.send_message(message.chat.id, 'Категории:', reply_markup=keyboard)
        else:
            await bot.send_message(message.chat.id, '❌ Список категорий пуст!')
    else:
        await bot.send_message(message.chat.id, '❌ Ошибка получения результатов по вашему запросу!')


async def send_show_result(message, show_code):
    await bot.send_chat_action(message.chat.id, 'typing')
    need_show = str(show_code)
    show_data_list = []
    if need_show == 'categories':
        show_data_list.append(['categories'])
        temp_data = get_categories()
        for item in temp_data:
            show_data_list.append(item)
    elif need_show == 'films':
        show_data_list.append(['films'])
        temp_data = get_films()
        for item in temp_data:
            show_data_list.append(item)
    else:
        show_data_list = ''
    if show_data_list != '':
        await show_items(message, show_data_list)
    else:
        await bot.send_message(message.chat.id, '❌ Ошибка получения результатов по вашему запросу!')


@bot.callback_query_handler(func=lambda call: True)
async def get_callback(query):
    data = query.data
    if data.startswith('/show_'):
        await bot.answer_callback_query(query.id)
        await send_show_result(query.message, query.data[6:])


@bot.callback_query_handler(func=lambda call: True)
async def callback_query(query):
    data = query.data
    if query.data == '/add_category':

        @bot.message_handler(func=lambda message: True)
        async def message_handler_add(message):
            new_category = str(message.text).strip()
            if new_category != '':
                if db_f.add_category(list(new_category)):
                    await bot.send_message(message.chat.id, f'✅ Категория "{new_category}" добавлена!')
                else:
                    await bot.send_message(message.chat.id, f'❌ Категория "{new_category}" не добавлена.')
            else:
                await bot.send_message(message.chat.id, f'❌ Новая категория не должна быть пустой!')


    # await bot.reply_to(message, 'Введите название категории')
    # @bot.message_handler(content_types=['text'])
    # def get_new_category(message):
    #     new_category = message.text.strip()
    #     db_funcs.add_category([new_category])
    #     bot.send_message(message.chat.id, f'Добавлена категория "{new_category}"!')
    # bot.register_poll_answer_handler(message, get_new_category)


@bot.message_handler(func=lambda message: True)
async def message_handler(message):
    message_list = str(message.text).strip().split()
    if len(message_list) == 2:
        film_name = message_list[0]
        film_year = message_list[1]
        if film_year.isdigit() and len(film_year) == 4:
            keyboard  = InlineKeyboardMarkup()
            keyboard .row_width = 2
            categories_list = get_categories()
            if len(categories_list) > 0:
                for cat in categories_list:
                    keyboard .add(InlineKeyboardButton(f'{cat}', callback_data=f'/add_category:{cat}'), )
                keyboard .add(InlineKeyboardButton(f'Добавить категорию', callback_data=f'/add_category'), )
            else:
                keyboard .add(InlineKeyboardButton(f'Добавить категорию', callback_data=f'/add_category'), )

            await bot.send_message(message.chat.id, 'Укажите категорию для фильма?', reply_markup=keyboard)
            await db_funcs.add_film([
                film_name,
                film_year,
                'film_category',
                0,
                get_timestamp(datetime.datetime.now()),
                '',
                0,
                False
            ])
            await bot.send_message(message.chat.id, f'Фильм "{film_name}" успешно добавлен!')
        else:
            await bot.send_message(message.chat.id, f'Вы указали:\nНазвание - {message_list[0]}\nГод - {message_list[1]}, но год должен быть корректным числом!')
    else:
        await bot.send_message(message.chat.id, f'Извини, я тебя не понял!')


if __name__ == '__main__':
    print('Бот запущен...')
    if not db_f.check_db_silent():
        result = db_f.create_db()
        print(f'{result[0]}, {result[1]}')

    if db_f.check_db_silent():
        asyncio.run(bot.infinity_polling())
    else:
        print('БД не найдена, бот не запущен!')