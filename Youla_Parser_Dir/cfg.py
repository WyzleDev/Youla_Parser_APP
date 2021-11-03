import logging
import os

from selenium.webdriver import FirefoxOptions


class ApplicationSettings:
    HOST_STORAGE: str = os.environ.get('HOST_STORAGE')

    PORT_STORAGE: int = os.environ.get("PORT_STORAGE")

    HUB_HOST: str = os.environ.get("HUB_HOST", '0.0.0.0')

    class Config:
        env_file = '.env'
        loger = logging.basicConfig(filename="logs.log", level=logging.INFO)
        PATH = 'https://youla.ru'

        ADDITIONAL_URL = '/moskva/nedvijimost'

        headers = {
            'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47',
            'Referer': 'https://youla.ru/'
        }

        db_collection_name = "Parser_Data"

        firefox_options = FirefoxOptions()
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('window-size=1200x600')

        attribute_dict = {
            "tip_sdelki": "task",
            "name": "name",
            "description": "text",
            "price": "cost",
            "realty_obshaya_ploshad": "totalarea",
            "realty_ploshad_kuhni": "kitchenarea",
            "komnat_v_kvartire": "roomquantity",
            "realty_etaj": "floor",
            "realty_etajnost_doma": "floors",
            "sobstvennik_ili_agent": "is_agent",
            "realty_building_type": "housing",
            "realty_hidden_location": "street",
            "posudomoechnaya_mashina": "dishWasher",
            "holodilnik": "refr",
            "remont": "repair",
            "lift": "cargoLift",
            "realty_god_postroyki": "buildYear",
        }


settings = ApplicationSettings()
