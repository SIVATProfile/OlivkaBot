import telegram
import telegram.ext
import requests
import os
import logging


class OlivkaBot(object):
    def __init__(self):
        self._logger = self._logger_setup(log_level="DEBUG")
        self._token = self._get_token()
        self._bot = telegram.Bot(token=self._token)
        self._logger.debug(f"Bot auth test answer: {self._bot.get_me()}")

    def _get_token(self):
        token = os.environ.get("API_TOKEN", None)
        if not token:
            self._logger.error(f"Environment variable 'API_TOKEN' not found")
            raise ValueError
        self._logger.debug(f"API TOKEN is {token}")
        return token

    @staticmethod
    def _logger_setup(log_level: str = "INFO") -> logging.Logger:
        logger = logging.getLogger()
        logger.setLevel(log_level)
        logger.propagate = False
        if not logger.hasHandlers():
            stream_handler = logging.StreamHandler()
            formatter = logging.Formatter(fmt=f"[%(asctime)s][%(levelname)-7s][%(funcName)s] %(message)s")
            logger.addHandler(stream_handler)
            stream_handler.setFormatter(formatter)
        return logger
