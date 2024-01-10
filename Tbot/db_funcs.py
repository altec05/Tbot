import os
import sqlite3
import variables as var
from path_funcs import create_path


# Создание базы данных и таблицы
def create_db():
    # проверка пути для файла БД
    try:
        os.makedirs(var.path_db, exist_ok=True)
    except Exception as e:
        print(f'Ошибка создания пути!\nОшибка: [{e}]')

    db = sqlite3.connect(var.path_db + '/Database.sqlite')
    cursor = db.cursor()

    try:
        # Создание таблицы Анекдоты
        cursor.execute('''CREATE TABLE IF NOT EXISTS anekdots (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            rate BOOLEAN,
            visible BOOLEAN NOT NULL
            )
            ''')
        db.commit()

        # Создание таблицы Просмотренные анекдоты
        cursor.execute('''CREATE TABLE IF NOT EXISTS anekdots_views (
                    user_id INTEGER PRIMARY KEY,
                    anekdots_id TEXT
                    )
                    ''')
        db.commit()

        db.close()
        return ('Создание таблицы', 'Таблица создана!')

    except Exception as e:
        db.close()
        return ('Создание таблицы', f'Ошибка создания таблицы!\n\nОшибка:\n[{e}]')
    finally:
        db.close()


# Список всех анекдотов
def get_anekdots_list():
    aneks_list = []
    try:
        with sqlite3.connect(var.path_db + '/Database.sqlite') as db:
            cursor = db.cursor()
            cursor.execute("""Select * from anekdots""")

            return cursor.fetchall()
    except:
        return False


# Добавить анекдот
def add_anekdot(anekdots_data: list):
    try:
        with sqlite3.connect(var.path_db + '/Database.sqlite') as db:
            cursor = db.cursor()
            cursor.execute("""INSERT INTO anekdots (title, body, visible) VALUES (?, ?, ?)""", anekdots_data)

            db.commit()
        return True
    except:
        return False


# Добавить просмотренный анекдот
def add_views_to_anekdots(anekdots_data: list):
    with sqlite3.connect(var.path_db + '/Database.sqlite') as db:
        cursor = db.cursor()
        for item in anekdots_data:
            cursor.execute(f"""INSERT INTO anekdots_views (user_id, anekdots_id) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET anekdots_id='{item[1]}'""", item)
        # cursor.executemany("""INSERT INTO anekdots_views VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET views=?""", anekdots_data)
        db.commit()
        return True


# Список всех просмотров анекдотов
def get_anekdots_views_list(user_id):
    aneks_list = []
    try:
        with sqlite3.connect(var.path_db + '/Database.sqlite') as db:
            cursor = db.cursor()
            cursor.execute("""Select * from anekdots_views WHERE user_id = ?""", [user_id])

            for item in cursor:
                temp_list = []
                for i in item:
                    try:
                        temp_list.append(int(i))
                    except:
                        temp_list.append(str(i))
                aneks_list.append(temp_list)

        return aneks_list
    except:
        return False


def clear_anekdot_views_for_user(user_id):
    try:
        send_str = ''
        send_list = [send_str, user_id]
        with sqlite3.connect(var.path_db + '/Database.sqlite') as db:
            cursor = db.cursor()
            cursor.execute("""UPDATE anekdots_views set anekdots_id = ? WHERE user_id = ?""", send_list)
            db.commit()
        return True
    except:
        return False


# Проверка существования таблицы без уведомлений
def check_db_silent():
    create_path()
    db = sqlite3.connect(var.path_db + '/Database.sqlite')
    cursor = db.cursor()

    try:
        cursor.execute("SELECT * FROM anekdots")
        res = cursor.fetchall()
        db.close()
        return True
    except:
        db.close()
        return False
    finally:
        db.close()


# Получить из БД просмотры
def get_views_from_bd():
    aneks_list = []
    try:
        with sqlite3.connect(var.path_db + '/Database.sqlite') as db:
            cursor = db.cursor()
            cursor.execute("""Select * from anekdots_views""")

            for item in cursor:
                aneks_list.append(item)
            return aneks_list
    except:
        return False