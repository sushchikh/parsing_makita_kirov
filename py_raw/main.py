from moduls import get_logger, get_links_1_lvl, get_links_2_lvl, list_2_lvl_uploader, get_links_3_lvl, get_products_dict
from moduls import dump_data_into_file, load_data_from_file, push_products_dict_tp_xlsx

if __name__ == '__main__':
    logger = get_logger()

    # grab the data:
    # links_1_lvl = get_links_1_lvl(logger)
    # links_2_lvl = get_links_2_lvl(logger, links_1_lvl)
    # links_2_lvl_full = list_2_lvl_uploader(logger, links_2_lvl)
    # links_3_lvl = get_links_3_lvl(logger, links_2_lvl_full)
    # dump_data_into_file(links_3_lvl)

    links_3_lvl = load_data_from_file()
    products_dict = get_products_dict(logger, links_3_lvl)

    # for key, value in products_dict.items():
    #     print(key, value)

    push_products_dict_tp_xlsx(logger, products_dict)
