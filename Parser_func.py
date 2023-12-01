import requests
from bs4 import BeautifulSoup
from pprint import pprint
from tqdm import tqdm
import sqlite3

# Требуемые характеристики квартир
PARAM_PATERN = (
    'Количество комнат', 'Площадь общая', 'Год постройки', 'Этаж / этажность', 'Тип дома', 'Область',
    'Населенный пункт', 'Улица', 'Район города', 'Координаты')
# URL сайта с которого парсим даные
URL = 'https://realt.by/sale/flats/'
# Данные для авторизации на сайте
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}


def get_last_page() -> int:
    """Функция определения последней страницы"""
    response = requests.get(URL, headers=HEADERS).text
    soup = BeautifulSoup(response, 'lxml')
    last_page = soup.find_all('a',
                              class_='focus:outline-none sm:focus:shadow-10bottom cursor-pointer select-none inline-flex font-normal text-body min-h-[2.5rem] min-w-[2.5rem] py-0 items-center !px-1.25 justify-center mx-1 hover:bg-basic-200 rounded-md disabled:text-basic-500')
    last_page = last_page[-1].text
    return int(last_page)


def get_all_links(last_page: int) -> list:
    """Функция для сбора ссылок объявлений квартир"""
    links = []
    for page in tqdm(range(1, last_page + 1), desc='parser_url: '):  # last_page + 1
        response = requests.get(f'{URL}?page={page}', headers=HEADERS)
        soup = BeautifulSoup(response.text, 'lxml')
        raw_links = soup.find_all('a', class_='z-1 absolute top-0 left-0 w-full h-full cursor-pointer', href=True)
        urls = [f'https://realt.by{el["href"]}' for el in raw_links]
        links.extend(urls)
    return links


def get_flats_data(links: list) -> dict:
    """Функция сбора данных по объявлениям квартир"""
    flats = {}

    for link in tqdm(links, desc='parsing_data:'):
        flat = {}
        resp = requests.get(link, headers=HEADERS)
        # flat_id = resp.url.split('/')[-1]
        s = BeautifulSoup(resp.text, 'lxml')
        flat_id = s.find('span', class_='flex-shrink-0 md:pr-1 md:flex').text.replace('ID ', '')

        # Название
        try:
            title = s.find('h1',
                           {
                               'class': 'order-1 mb-0.5 md:-order-2 md:mb-4 block w-full !inline-block lg:text-h1Lg text-h1 font-raleway font-bold flex items-center'}).text
        except Exception as e:
            title = ''
            print(flat_id)

        # Стоимость
        try:
            price = s.find('span', {'class': 'text-subhead sm:text-body text-basic inline-block'}).text.replace('≈',
                                                                                                                '').replace(
                ' ', '').replace('$', '').replace(' ', '')
        except Exception as e:
            price = -1

        # Картинка
        try:
            picture = s.find('div', class_='absolute inset-0').find_all('img')[1]['src']
        except Exception as e:
            picture = ''

        # Описание
        try:
            discription = s.find('div', class_=['description_wrapper__tlUQE']).text
        except Exception as e:
            discription = ''

        # Сохранение результатов
        flat['title'] = title
        flat['price'] = int(price)
        flat['picture'] = picture
        flat['discription'] = discription

        # Характеристики
        try:
            raw_params = s.find_all('li', class_='relative py-1')
            for param in raw_params:
                try:
                    key = param.find('span').text
                except Exception as e:
                    key = ''
                if key not in PARAM_PATERN:
                    continue
                value = param.find(['p', 'a']).text.replace('г. ', '').replace(' м²', '')
                if value.isdigit():
                    value = int(value)
                flat[key] = value
        except Exception as e:
            print(flat_id)
        flats[flat_id] = flat
    return flats


def connection_db():
    """Подключение к БД"""
    connection = sqlite3.connect('realt_by_flats.db')
    return connection


def create_table_db():
    """Создание таблицы"""
    connection = connection_db()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_flats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flat_id TEXT unique,
        title TEXT,
        price INTEGER,
        picture TEXT,
        discription TEXT,
        year TEXT,
        rooms TEXT,
        coordinates TEXT,
        locality TEXT,
        region TEXT,
        square TEXT,
        district TEXT,
        type TEXT,
        street TEXT,
        floor TEXT
        )
        """)


def database_loading(data: dict):
    """Запись данных в БД"""
    connection = connection_db()
    cursor = connection.cursor()
    params = ('title', 'price', 'picture', 'discription', 'Год постройки', 'Количество комнат', 'Координаты',
              'Населенный пункт', 'Область', 'Площадь общая', 'Район города', 'Тип дома', 'Улица', 'Этаж / этажность')
    for el_s in data:
        data_flat = []
        data_flat.append(el_s) #добавляем id квартиры в список
        for el in params:
            if not el in data[el_s]: # проверяем есть ли хараетеристика в объявлении, если есть добавляем значение, если нет то пустую строку
                data_flat.append('')
            else:
                data_flat.append(data[el_s][el])
        data_flat = tuple(data_flat)
        insert_db = """
            INSERT INTO data_flats(
                flat_id,
                title,
                price,
                picture,
                discription,
                year,
                rooms,
                coordinates,
                locality,
                region,
                square,
                district,
                type,
                street,
                floor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        cursor.execute(insert_db, (data_flat))
        connection.commit()
    connection.close()

def database_loading2(data: dict):
    """Запись данных в БД"""
    connection = connection_db()
    cursor = connection.cursor()



    params = ('title', 'price', 'picture', 'discription', 'Год постройки', 'Количество комнат', 'Координаты',
              'Населенный пункт', 'Область', 'Площадь общая', 'Район города', 'Тип дома', 'Улица', 'Этаж / этажность')
    for el_s in data:
        data_flat = []
        data_flat.append(el_s)
        for el in params:
            if not el in data[el_s]:
                data_flat.append('')
            else:
                data_flat.append(data[el_s][el])
        data_flat = tuple(data_flat)
        pprint(data_flat)
        insert_db = """
            INSERT INTO data_flats(
                flat_id,
                title,
                price,
                picture,
                discription,
                year,
                rooms,
                coordinates,
                locality,
                region,
                square,
                district,
                type,
                street,
                floor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        cursor.execute(insert_db, (data_flat))
        connection.commit()
    connection.close()


def data_output():
    """Функция вывода данных из БД"""
    connection = connection_db()
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM  data_flats""")
    data = cursor.fetchall()
    return data
    # print(data)


def run_parser():
    last_page = get_last_page()
    links = get_all_links(last_page)
    data = get_flats_data(links)
    # pprint(data)
    connection_db()
    create_table_db()
    database_loading(data)

# run_parser()
# pprint(data_output(connection_db()))
