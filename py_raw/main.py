from moduls import get_links_1_lvl, get_logger

if __name__ == '__main__':
    logger = get_logger()
    links_1_lvl = get_links_1_lvl(logger)

    print(links_1_lvl)
