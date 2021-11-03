import pymongo
import logging
from cfg import settings
import datetime


class Storage:

    def __init__(self):
        self.client = pymongo.MongoClient(host=settings.HOST_STORAGE, port=settings.PORT_STORAGE)
        self.database = self.client[settings.Config.db_collection_name]
        self.urls = self.database.urls
        self.card_info = self.database.card_info

    def write_data_urls(self, data_to_write):
        if type(data_to_write) == dict:
            self.urls.insert_one(data_to_write)
        else:
            logging.info('[-] Exiting! Type of the data is not a dict!' + f'{datetime.datetime.now()}')
            exit(1)

    def write_data_info(self, info_to_write):
        if type(info_to_write) == dict:
            self.card_info.insert_one(info_to_write)
        else:
            logging.info('[-] Exiting! Type of the data is not a dict!' + f'{datetime.datetime.now()}')
            exit(1)

    def get_links(self) -> pymongo.collection.Collection:
        return self.database["urls"].find()

    def get_data(self) -> pymongo.collection.Collection:
        return self.database["card_info"].find()
