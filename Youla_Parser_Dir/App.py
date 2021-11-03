import datetime
import logging
from parser_core import Parser


class Application:
    def __init__(self):
        self.parser = Parser()
        logging.info('Application has been started ' + f'{datetime.datetime.now()}')

    def run(self):
        """Функция запуска приложенич"""
        self.parser.parse_cards_info()

    @staticmethod
    def stop() -> None:
        """Функия остановки всех процессов и функция приложения"""
        logging.info('[!]Switching off....')
        exit(0)
