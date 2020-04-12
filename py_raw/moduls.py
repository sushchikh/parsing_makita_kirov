import requests
import yaml
import logging.config
import pickle
from datetime import datetime
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from time import sleep
import pandas as pd

"""
• go to makita.kirov.ru
• grab links from "категории", push it to the list "links_1_lvl"
• go to each link in links_1_lvl list, grab links, push it to the list "links_2_lvl"
• go to each links in links_2_lvl, check for pagination, if no pagination — push this links to links_3_lvl
  if there is pagination — grab the number of all pagination pages, add it to the link (in loop), push it to the 
  links_3_lvl
• go to each item in links_3_lvl, grab name, link, price. Push it to the dict,
• push dict to the xlsx-file with , decorate it
"""


######## ##     ## ######## ##     ## ########  ########  ######
##       ##     ##    ##    ##     ## ##     ## ##       ##    ##
##       ##     ##    ##    ##     ## ##     ## ##       ##
######   ##     ##    ##    ##     ## ########  ######    ######
##       ##     ##    ##    ##     ## ##   ##   ##             ##
##       ##     ##    ##    ##     ## ##    ##  ##       ##    ##
##        #######     ##     #######  ##     ## ########  ######


# --------------------------------------------------------------------------------------------
# create and return logger
def get_logger():
    """return logger_object with parametrs from config.yaml"""
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    return logger

# --------------------------------------------------------------------------------------------
# cut all except numbers
def price_cutter(text):
    output_text = ''
    for i in text:
        if i.isdigit():
            output_text += i
    return output_text


# --------------------------------------------------------------------------------------------
# dump data into a file
def dump_data_into_file(data):
    with open ('./../data/data', 'wb') as f:
        pickle.dump(data, f)


# --------------------------------------------------------------------------------------------
# load data from file
def load_data_from_file():
    with open('./../data/data', 'rb') as f:
        data = pickle.load(f)
    return data

########     ###    ########   ######  ######## ########
##     ##   ## ##   ##     ## ##    ## ##       ##     ##
##     ##  ##   ##  ##     ## ##       ##       ##     ##
########  ##     ## ########   ######  ######   ########
##        ######### ##   ##         ## ##       ##   ##
##        ##     ## ##    ##  ##    ## ##       ##    ##
##        ##     ## ##     ##  ######  ######## ##     ##


def get_links_1_lvl(logger):
    print('start grab links_1_lvl')
    links_1_lvl = []
    session = requests.Session()
    request = session.get(url='http://makita.kirov.ru')
    if request.status_code == 200:
        soup = bs(request.content, 'html.parser', from_encoding="iso-8859-1")
        category_raw_links = soup.select('#column-left > div > div.box-content > div > ul > li > a')
        for i in category_raw_links:
            url_1_lvl = i.get('href')
            links_1_lvl.append(url_1_lvl)
    else:
        logger.error('module - "get_links_1_lvl", error with connection to http://makita.kirov.ru')
    print('end grab links_1_lvl')
    return links_1_lvl


def get_links_2_lvl(logger, links_1_lvl: list):
    links_2_lvl = []
    session = requests.Session()
    for i in tqdm(links_1_lvl):
        request = session.get(i)
        if request.status_code == 200:
            soup = bs(request.content, 'html.parser', from_encoding="iso-8859-1")
            category_raw_links = soup.select('#column-left > div > div.box-content > div > ul > '
                                             'li.active > ul > li > a')
            for j in category_raw_links:
                url_2_lvl = j.get('href')
                links_2_lvl.append(url_2_lvl)
        else:
            logger.error(f'module - "get_links_2_lvl", error with connection to {i}]')
    return links_2_lvl


def list_2_lvl_uploader(logger, links_2_lvl: list):
    session = requests.Session()
    for i in tqdm(links_2_lvl):
        request = session.get(i)
        if request.status_code == 200:
            soup = bs(request.content, 'html.parser', from_encoding="iso-8859-1")
            if soup.select('div.box-subcat'):  # if there is subcategory
                subcat_page_link = soup.select('#content > div.box > div.box-content > '
                                               'div > ul > li > div.name.subcatname > a')
                for _ in subcat_page_link:
                    links_2_lvl.append(_.get('href'))
    return links_2_lvl


def get_links_3_lvl(logger, links_2_lvl: list):
    links_3_lvl = []
    session = requests.Session()
    for i in tqdm(links_2_lvl):
        request = session.get(i)
        if request.status_code == 200:
            soup = bs(request.content, 'html.parser', from_encoding="iso-8859-1")
            list_of_pagination = soup.select('#content > div.pagination > div.links > a')
            if len(list_of_pagination) == 0:  # if no pagination, take url to the third lvl
                links_3_lvl.append(i)
            elif len(list_of_pagination) >= 1:  # if there is some pagination, find last and add loop to the third lvl
                links_3_lvl.append(i)
                last_page_in_pagination = str(list_of_pagination[1].get('href'))[-1]
                for _ in range(1, int(last_page_in_pagination)):
                    url_3_lvl = str(i) + '&page=' + last_page_in_pagination
                    links_3_lvl.append(url_3_lvl)
        else:
            logger.error(f'module - "get_links_3_lvl", error with connection to {i}]')
    return links_3_lvl


def get_products_dict(logger, links_3_lvl: list):
    list_of_product_names = []
    list_of_product_prices = []
    list_of_product_links = []
    products_dict = {}
    session = requests.Session()
    for i in tqdm(links_3_lvl):
        request = session.get(i)
        if request.status_code == 200:
            soup = bs(request.content, 'html.parser', from_encoding="UTF-8")
            # print(soup)
            raw_items_names_and_links = soup.select('div.name > a')
            # '#content > div.product-list > div:nth-child(1) > div.left > div.name > a'
            raw_item_price = soup.select('div.price')
            # print('raw_items:', raw_items_names_and_links)
            # print('raw_item_price', raw_item_price)
            x = len(raw_items_names_and_links) - len(raw_item_price)
            raw_items_names_and_links_without_subcategory = raw_items_names_and_links[x::]

            for j in raw_items_names_and_links_without_subcategory:
                list_of_product_names.append(str(j.get_text()))
                list_of_product_links.append(j.get('href'))
            for k in raw_item_price:
                list_of_product_prices.append(int(price_cutter(k.get_text())))
            # print(list_of_product_names)
            # print(list_of_product_links)

            if ((len(list_of_product_names) == len(list_of_product_links)) and
                    (len(list_of_product_names) == len(list_of_product_prices))):
                for _ in range(len(list_of_product_names)):
                    products_dict[_] = [list_of_product_names[_], list_of_product_links[_], list_of_product_prices[_]]
            else:
                print(f'on page {i} there is miss some value (perhaps price')
                return {'something': ['wrong', 'in page']}
        else:
            logger.error(f'module - "get_products_dict", error with connection to {i}]')
    # print(list_of_product_prices)
    return products_dict


def push_products_dict_tp_xlsx(logger, data):
    products_dict_df_not_transpon = pd.DataFrame(data)
    products_dict_df = products_dict_df_not_transpon.T
    products_dict_df_sort = products_dict_df.sort_values(by= [0])
    today = datetime.today()
    name = './../xlsx/makita_price_' + today.strftime("%d.%m.%Y") + '.xlsx'
    writer = pd.ExcelWriter(name, engine='xlsxwriter')
    products_dict_df_sort.to_excel(writer, sheet_name='Sheet1', index=False)
    workbook = writer.book
    cell_format = workbook.add_format({
        'bold': True,
        'font_color': 'black',
        'align': 'center',
        'valign': 'center',
        'bg_color': '#ecf0f1'
    })
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column('A:A', 60)
    worksheet.set_column('B:B', 9)
    worksheet.set_column('C:D', 17)
    worksheet.write('A1', 'Название', cell_format)
    worksheet.write('B1', 'Cсылка', cell_format)
    worksheet.write('C1', 'Цена (р.)', cell_format)
    worksheet.write('D1', 'Наш код', cell_format)
    worksheet.freeze_panes(1, 0)
    writer.save()