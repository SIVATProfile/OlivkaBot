import telegram
import requests
import os


class OlivkaBot(object):
    def __init__(self):
        self._token = self._get_token()
        self._bot = telegram.Bot(token=self._token)

    @staticmethod
    def _get_token():
        token = os.environ.get("API_TOKEN", None)
        if not token:
            print(f"Environment variable 'API_TOKEN' not found")
            raise ValueError
        return token
