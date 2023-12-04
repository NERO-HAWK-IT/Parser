import sqlite3
def connection_db(name_db:str):
    """Подключение к БД
    name_db - наименование БД"""
    connection = sqlite3.connect(name_db)
    return connection

def create_table_db(name_db:str,name_table:str,attributes: dict):
    """Создание таблицы БД.
    name_db - наименвоание БД (текст: наименвоание.db)
    name_table - наименование таблицы БД (текст: наименование)
    attributes - словарь с необходимыми атрибутами"""
    connection = connection_db(name_db)
    try:
        cursor = connection.cursor()
        table_attributes = 'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        for el in attributes:
            table_attributes += f'{el} {attributes[el]},'
        table_attributes = table_attributes.strip(',')
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {name_table}({table_attributes})""")
    except sqlite3.DatabaseError as err:
        print('Error:', err)

def database_loading(name_db:str,name_table:str,attributes: dict, data :list):
    """Запись данных в БД.
    name_db - наименвоание БД (текст: наименвоание.db)
    name_table - наименование таблицы БД (текст: наименование)
    attributes - словарь с необходимыми атрибутами
    data - спиок словарей с данными"""
    connection = connection_db(name_db)
    try:
        cursor = connection.cursor()
        table_attributes = ''
        for el in attributes:
            table_attributes += f'{el},'
        table_attributes = table_attributes.strip(',')
        table_values_attributes =''
        for el in attributes:
            table_values_attributes += f':{el},'
        table_values_attributes = table_values_attributes.strip(',')
        cursor.execute(f"""
        INSERT INTO {name_table}({table_attributes})
        VALUES ({table_values_attributes})""", data)
    except sqlite3.DatabaseError as err:
        print('Error:', err)
    else:
        connection.commit()
        connection.close()

