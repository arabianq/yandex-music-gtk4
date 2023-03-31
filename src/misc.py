import urllib3
from urllib3.exceptions import MaxRetryError


def has_internet():
    try:
        urllib3.PoolManager().request("GET", "http://music.yandex.ru")
    except MaxRetryError:
        return False
    return True
