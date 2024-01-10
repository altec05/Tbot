import os
import variables as var

# проверка пути для файла БД
def create_path():
    try:
        os.makedirs(var.path_db, exist_ok=True)
    except Exception as e:
        print('Создание пути для Базы данных', f'Ошибка создания пути!\nОшибка: [{e}]')