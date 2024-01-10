from telebot.types import  InlineKeyboardMarkup, InlineKeyboardButton

main_menu = InlineKeyboardMarkup()
main_menu.row_width = 1
main_menu.add(InlineKeyboardButton('Анекдот', callback_data='/get_anekdot'),
              InlineKeyboardButton('Добавить анекдот', callback_data='/add_anekdot'))
