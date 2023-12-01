import requests
from bs4 import BeautifulSoup
from pprint import pprint
from tqdm import tqdm

PARAM_PATERN=('Количество комнат', 'Площадь общая', 'Год постройки', 'Этаж / этажность', 'Тип дома', 'Область', 'Населенный пункт', 'Улица', 'Район города', 'Координаты')
url = 'https://realt.by/sale/flats/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}
# response = requests.get(url, headers=headers)
# with open('test.html', 'w', encoding='utf-8') as file:
#     file.write(response.text)


with open('test.html', encoding='utf-8') as file:
    data = file.read()
soup = BeautifulSoup(data, 'lxml')
raw_links = soup.find_all('a', class_='z-1 absolute top-0 left-0 w-full h-full cursor-pointer', href=True)
links = []
for el in raw_links:
    link = f'https://realt.by{el["href"]}'
    links.append(link)

flats = []

for link in tqdm(links, desc='parsing_data:'):
    flat={}
    resp = requests.get(link, headers=headers)
    s = BeautifulSoup(resp.text, 'lxml')
## Название
    title = s.find('h1',
                   {
                       'class': 'order-1 mb-0.5 md:-order-2 md:mb-4 block w-full !inline-block lg:text-h1Lg text-h1 font-raleway font-bold flex items-center'}).text
## Стоимость
    try:
        price = s.find('span', {'class': 'text-subhead sm:text-body text-basic inline-block'}).text.replace('≈',
                                                                                                            '').replace(
            ' ', '').replace('$', '').replace(' ', '')
    except Exception as e:
        price = -1

## Картинка
    picture = s.find('div', class_='absolute inset-0').find_all('img')[1]['src']

## Описание
#     discription = s.find('section', {'class': 'bg-white flex flex-wrap md:p-6 my-4 rounded-md'}).text
    try:
        discription = s.find('div', class_= ['description_wrapper__tlUQE']).text
    except Exception as e:
        discription = ''

# ## Характеристики
#     discription_flat_key = []
#     discription_flat_value = []
#
#     for el in s.find('ul', class_='w-full -my-1').find_all('span'):
#         discription_flat_key.append(el.text)
#     for el in s.find('ul', class_='w-full -my-1').find_all('p'):
#         discription_flat_value.append(el.text)
#
#     discription_flat = dict(zip(discription_flat_key, discription_flat_value))
#
# ## Характеристики расположения
#     discription_adress_key = []
#     discription_adress_value = []
#
#     for el in s.find('ul', class_='w-full mb-0.5 -my-1').find_all('span'):
#         discription_adress_key.append(el.text)
#     for el in s.find('ul', class_='w-full mb-0.5 -my-1').find_all('a'):
#         discription_adress_value.append(el.text.replace(' ',''))
#
#     discription_adress = dict(zip(discription_adress_key, discription_adress_value))

# # Характеристики 2 вариант
    raw_params = s.find_all('li', class_='relative py-1')
    params = dict()
    for param in raw_params:
        key = param.find('span').text
        if key not in PARAM_PATERN:
            continue
        value = param.find(['p','a']).text.replace('г. ', '').replace(' м²','')
        if value.isdigit():
            value = int(value)
        params[key] = value
pprint(params)

## Сохранение результатов
    # flat['title'] = title
    # flat['price'] = int(price)
    # flat['picture'] = picture
    # flat['discription'] = discription
    # flat['params'] = params
    # flats.append(flat)

# pprint(flats)

# ВЫВОД РЕЗУЛЬТАТА
#     print(f'{title} - {price} $\n{discription}\n{picture}\n\n Характеристики:')
#     for el in discription_flat:
#         print(f'{el} - {discription_flat[el]}')
#     print('\n Местоположение:')
#     for el in discription_adress:
#         print(f'{el} - {discription_adress[el]}')

