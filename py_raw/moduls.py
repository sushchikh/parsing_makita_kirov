import requests
import tqdm
import yaml
import logging.config
from datetime import datetime
from bs4 import BeautifulSoup as bs
from time import monotonic

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
# созадет и возвращает логгер для логирования в файл
def get_logger():
    """return logger_object with parametrs from config.yaml"""
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    return logger






########     ###    ########   ######  ######## ########
##     ##   ## ##   ##     ## ##    ## ##       ##     ##
##     ##  ##   ##  ##     ## ##       ##       ##     ##
########  ##     ## ########   ######  ######   ########
##        ######### ##   ##         ## ##       ##   ##
##        ##     ## ##    ##  ##    ## ##       ##    ##
##        ##     ## ##     ##  ######  ######## ##     ##


def get_links_1_lvl(logger):
    links_1_lvl = []
    session = requests.Session()
    request =session.get(url='http://makita.kirov.ru')
    if request.status_code == 200:
        soup = bs(request.content, 'html.parser')
        category_raw_links =soup.select('#column-left > div > div.box-content > div > ul > li > a')
        for i in category_raw_links:
            url_1_lvl = i.get('href')
            links_1_lvl.append(url_1_lvl)
    else:
        logger.error('modul - "get_links_1_lvl", error with connection to http://makita.kirov.ru')
    return links_1_lvl

