import sqlite3

import db_funcs
from variables import path_db


def add_item(item_data):
    if not db_funcs.check_db_silent():
        db_funcs.create_db()
    db = sqlite3.connect(path_db + '/Films.sqlite')
    try:
        cursor = db.cursor()

        cursor.execute(
            "INSERT OR IGNORE INTO films (name, year_from, category, rating, date_of_add, description, my_rate, status)"
            "VALUES(?, ?, ?, ?, ?, ?, ?, ?)", item_data)
        changes = db.total_changes

        db.commit()
        return True
    except:
        return False
    finally:
        db.close()
