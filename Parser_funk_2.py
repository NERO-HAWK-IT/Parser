import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pprint import pprint
import sqlite3
import db_client

# URL страницы раздела сайта с которого парсим данные
URL = 'https://realt.by/sale/flats/'

# URL страницы сайта с которого парсим данные
URL_page = 'https://realt.by/sale/flats/?page='

# Данные для авторизации на сайте
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}

# Словарь запрашиваемых параметров квартир с типом значений
Apartment_parameters = {'flat_id': 'INTEGER',
                        'title': 'TEXT',
                        'price': 'INTEGER',
                        'picture': 'TEXT',
                        'discription': 'TEXT',
                        'rooms': 'INTEGER',
                        'square': 'INTEGER',
                        'year': 'INTEGER',
                        'floor': 'INTEGER',
                        'type_building': 'TEXT',
                        'region': 'TEXT',
                        'locality': 'TEXT',
                        'street': 'TEXT',
                        'house_number': 'INTEGER',
                        'district': 'TEXT',
                        'microdistrict': 'TEXT',
                        'coordinates': 'TEXT',
                        'phone_number': 'TEXT'}


def get_html_page():
    """Поиск скрытых объявлений realt.by"""
    response = requests.get(f'{URL_page}1', headers=HEADERS).text
    with open('test_page1.html', 'w', encoding='utf-8') as f:
        f.write(response)
    # т.к. realt.by на странице отображает 30 объявлений а при парсинге достается только 20, при этом когда скролим
    # страницу ничего не подкружается в (network/сеть), то мы из полученного кода ищем скрытый код и из него берем нужный тэг
    soup = BeautifulSoup(response, 'lxml').find('script', id='__NEXT_DATA__').text
    data = json.loads(json.loads(soup)['props']['pageProps']['initialState']['objectsListing']['objects'])

    with open('test1.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))  # Преобразуем полученный код в читабельный вид
    print(len(data))


# get_html_page()

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
    for page in tqdm(range(1, last_page + 1), desc='Parser_url: '):
        page_link = f'{URL_page}{page}'
        links.extend([page_link])
    return links


def get_flats_data(links: list, parametrs:dict) -> list:
    """Функция сбора данных по объявлениям квартир"""
    flats = []
    for link in tqdm(links, desc='Parsing_data'):
        response = requests.get(link, headers=HEADERS).text
        soup = BeautifulSoup(response, 'lxml').find('script', id='__NEXT_DATA__').text
        data = json.loads(soup)['props']['pageProps']['initialState']['objectsListing']['objects']
        for el in data:
            flat = parametrs.copy()
            code_params = {'flat_id': 'code',
                           'title': 'title',
                           'price': 'price',
                           'picture': 'images',
                           'discription': 'description',
                           'rooms': 'rooms',
                           'square': 'areaTotal',
                           'year': 'buildingYear',
                           'floor': 'storey',
                           'type_building': 'houseType',
                           'region': 'stateRegionName',
                           'locality': 'townName',
                           'street': 'streetName',
                           'house_number': 'houseNumber',
                           'district': 'townDistrict',
                           'microdistrict': 'microdistrict',
                           'coordinates': 'location',
                           'phone_number': 'contactPhones'}
            dict_house_type = {0: 'Кирпичный', 1: 'Панельный', 2: 'Блок-комнаты', 3: 'Монолитный', 4: '',
                               5: 'Силикатные блоки', 6: 'Бревенчатый', 7: '', 8: '', 9: 'Блочный', 10: 'Деревянный',
                               11: 'Каркасно-блочный', 12: 'Каркасно-кирпичный', 13: 'Каркасный',
                               14: 'Кирпично-блочный',
                               15: 'Кирпично-деревянный', 16: 'Монолитно-блочный'}

            for par in code_params:
                try:
                    flat[par] = el[code_params[par]]
                except Exception as e:
                    flat[par] = ''
            try:
                flat['coordinates'] = str(flat['coordinates'][0]) + ', ' + str(flat['coordinates'][1])
            except Exception:
                flat['coordinates'] = ''
            try:
                flat['picture'] = str(flat['picture'][0])
            except Exception:
                flat['picture'] = ''
            try:
                flat['phone_number'] = str(flat['phone_number'][0])
            except Exception:
                flat['phone_number'] = ''
            try:
                for tb in dict_house_type:
                    if tb == flat['type_building']:
                        flat['type_building'] = dict_house_type[tb]
            except Exception:
                flat['type_building'] = ''
            flats.append(flat)

    # for flat in tqdm(flats, desc='Parametr_2'): # поиск параметров Район и микрорайон
    #         resp = requests.get(f'https://realt.by/sale-flats/object/{flat["flat_id"]}/', headers=HEADERS)
    #         sou = BeautifulSoup(resp.text, 'lxml')
    #         par2 = sou.find('section',
    #                        {'id': 'map', 'class': 'bg-white flex flex-wrap md:p-6 my-4 rounded-md'}).find_all('li',
    #                                                                                                           class_='relative py-1')
    #         for par in par2:
    #             try:
    #                 key = par.find('span').text
    #             except Exception as e:
    #                 key = ''
    #             if key == 'Район города':
    #                 flat['district'] = par.find('a').text
    #             if key == 'Микрорайон':
    #                 flat['microdistrict'] = par.find('a').text
    # pprint(flats)

    return flats

def run_parser():
    last_page = get_last_page()
    links = get_all_links(last_page)
    data = get_flats_data(links, Apartment_parameters)

    db_client.create_table_db('realt_by_flats-3.db', 'flats_data', Apartment_parameters)
    for el in tqdm(data, desc='Loading data in DB:'):
        db_client.database_loading('realt_by_flats-3.db', 'flats_data', Apartment_parameters, el)

run_parser()
