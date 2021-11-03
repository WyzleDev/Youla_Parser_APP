import datetime
import logging
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
from cfg import settings
from typing import List
from storage_core import Storage
from selenium.common.exceptions import StaleElementReferenceException

import re
import hashlib
import json


class Parser:
    def __init__(self):
        self.__how_many_attempts = 2
        print(settings.HUB_HOST)
        self.__driver = webdriver.Remote(command_executor=f"http://selenium-hub:4444/wd/hub",
                                         desired_capabilities={"browserName": "firefox", "javascriptEnabled": True},
                                         keep_alive=True,
                                         options=settings.Config.firefox_options)
        self.headers = settings.Config.headers
        self.url = settings.Config.PATH + settings.Config.ADDITIONAL_URL
        self.storage = Storage()
        logging.info('Class parser has been inited' + f'{datetime.datetime.now()}')

    def get_html_page(self, url_to_parse) -> str:
        """Функция, которая возвращает html раметку страницы сайта: https://youla.ru/moskva/nedvijimost"""
        last_height = self.__driver.execute_script("return document.body.scrollHeight")
        while self.__how_many_attempts > 0:
            self.__driver.get(url=url_to_parse)
            self.__how_many_attempts -= 1
        while True:
            self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(5)

            new_height = self.__driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        html_page = self.__driver.page_source

        logging.info('got an html of page' + f'{datetime.datetime.now()}')

        return html_page

    def get_urls_of_cards(self) -> List:
        """Функция, которая парсит ссылки на карточки объектов недвижимости и возвращает их список"""
        links_list = list()

        page = self.get_html_page(url_to_parse=self.url)
        link_parser_soup = BeautifulSoup(page, 'html.parser')
        elements = link_parser_soup.find_all('li', class_='product_item')

        for e in elements:
            links_list.append(settings.Config.PATH + e.find_next('a')['href'])

        _links = {
            'urls': f'{links_list}'
        }

        logging.info('Got links of cards ' + f'{datetime.datetime.now()}')

        self.storage.write_data_urls(_links)
        print(len(links_list))
        return links_list

    def parse_cards_info(self) -> None:

        """Функция, которая парсит информацию с каждой карточки по полученной ссылке"""
        links_of_cards = self.get_urls_of_cards()

        for link in links_of_cards:
            try:
                self.__driver.get(url=link)
                logging.info('Перехожу по ссылке на карточку объекта.')
            except WebDriverException:
                links_of_cards.remove(link)
                logging.info(
                    'Redirecting to promo-url, deleting this url from list of urls' + f'{datetime.datetime.now()}')
                continue
            js = '__YOULA_STATE__.entities.products[0]'
            res = self.__driver.execute_script(f'return {js}')
            ad_dict2 = {
                "url": link,
                "id": hashlib.md5(link.encode('utf-8')).hexdigest()
            }
            ad_dict = dict()
            ad_dict["forum_id"] = 1
            ad_dict["phone"] = ''
            ad_dict["idCountry"] = -1
            ad_dict["idRegion"] = -1
            ad_dict["idDistrict"] = -1
            ad_dict["idCity"] = -1
            ad_dict["currency_mortgage"] = 0

            ad_dict2['content'] = json.dumps(ad_dict, indent=5)
            try:
                for i in ["id", "name", "description", "location", "price", "images"]:
                    if i in res.keys():
                        if i == "name":
                            ad_dict[settings.Config.attribute_dict[i]] = res[i]
                            if "Квартира" in res[i]:
                                ad_dict["type"] = 1
                            elif "Комната" in res[i]:
                                ad_dict["type"] = 2
                            elif "Дом" in res[i] or "Участок" in res[i]:
                                ad_dict["type"] = 3
                            elif "свободного назначения" in res[i]:
                                ad_dict["type"] = 4
                            elif "Гараж" in res[i]:
                                ad_dict["type"] = 5
                            else:
                                ad_dict["type"] = 0
                        elif i == "description":
                            ad_dict[settings.Config.attribute_dict[i]] = res[i]
                        elif i == "location":
                            ad_dict["latitude"] = res[i]["latitude"]
                            ad_dict["longitude"] = res[i]["longitude"]
                        elif i == "price":
                            ad_dict[settings.Config.attribute_dict[i]] = res[i] // 100
                        elif i == "images":
                            ad_dict["images"] = ";".join([i['url'] for i in res[i]])
            except TypeError as tp:
                logging.info(f'{tp}' + f'{datetime.datetime.now()}')
                links_of_cards.remove(link)
                continue

            for i in res['attributes']:
                attr_name = i['slug']
                if attr_name in settings.Config.attribute_dict.keys():
                    if attr_name in ["realty_obshaya_ploshad", "realty_ploshad_kuhni"]:
                        ad_dict[settings.Config.attribute_dict[attr_name]] = int(i['rawValue']) // 100

                    elif attr_name in ["realty_etaj", "realty_etajnost_doma"]:
                        ad_dict[settings.Config.attribute_dict[attr_name]] = int(i['rawValue'])

                    elif attr_name == "sobstvennik_ili_agent":
                        ad_dict[settings.Config.attribute_dict[attr_name]] = (0 if i['rawValue'] == 'Собственник' else 1)

                    elif attr_name == "tip_sdelki":
                        if i['rawValue'] == "Продажа":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 1
                        elif i['rawValue'] == "Аренда":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 2
                        else:
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 0

                    elif attr_name == "realty_building_type":
                        if i['rawValue'] == "Новостройка":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 1
                        elif i['rawValue'] == "Вторичка":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 2
                        else:
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 0

                    elif attr_name in ["holodilnik", "posudomoechnaya_mashina"]:
                        if i["rawValue"] == "Есть":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 1
                        else:
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 0

                    elif attr_name == "remont":
                        if i["rawValue"] == "Без отделки":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 1
                        elif i["rawValue"] == "Чистовая отделка":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 2
                        elif i["rawValue"] == "Муниципальный ремонт":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 3
                        elif i["rawValue"] == "Хороший ремонт":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 4
                        elif i["rawValue"] == "Евроремонт":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 5
                        elif i["rawValue"] == "Эксклюзивный":
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 6
                        else:
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 0
                    elif attr_name == "lift":
                        if i['rawValue'] in ["Легковой и грузовой", "Грузовой", "Легковой"]:
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 1
                        else:
                            ad_dict[settings.Config.attribute_dict[attr_name]] = 0

                    elif attr_name == "realty_god_postroyki":
                        ad_dict[settings.Config.attribute_dict[attr_name]] = int(i['rawValue'])
                    elif attr_name == "realty_hidden_location":
                        ad_dict[settings.Config.attribute_dict[attr_name]] = i['rawValue']
            # values_of_headers = soup2.find_all("li", class_='sc-pcYTN')[2].find_all('dd', class_='sc-AxjAm')

            button = self.__driver.find_elements_by_class_name('sc-fzokvW')

            if len(button) == 5:
                button[4].click()
            elif len(button) == 7:
                button[5].click()

            phone = self.__driver.find_elements_by_tag_name('p')

            try:
                for p in phone:
                    if re.match("(\W\d{1}) (\W\d{3}\W) (\d{3})-(\d{2})-(\d{2})", f'{p.text}'):
                        ad_dict['phone'] = p.text
            except StaleElementReferenceException as SE:
                continue
            ad_dict2["content"] = json.dumps(ad_dict, ensure_ascii=False)

            ad3 = ad_dict2
            self.storage.write_data_info(ad3)
            links_of_cards.remove(link)

        self.__driver.close()


