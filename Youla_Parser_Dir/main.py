#!/usr/bin/env python
import logging
from App import Application
from pymongo.errors import ConfigurationError


def main():
    app.run()


if __name__ == "__main__":
    app = Application()
    try:
        main()
    except ConfigurationError as CE:
        logging.debug(f"[-]{CE}")
        logging.debug(f'[+]Retrying')
        print('Retrying')
        main()
