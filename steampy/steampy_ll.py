# -*- coding: utf-8 -*-
import re
import os
import requests
from bs4 import BeautifulSoup


THRESHOLD = 50
STEAM_ID = '76561197987677089'
LOCALE = 'ee'

STEAM_STORE_URL = "https://store.steampowered.com/app/"
WISHLIST_URL = "http://steamcommunity.com/profiles/{}/wishlist"
NEXMO_SMS_URL = "https://rest.nexmo.com/sms/json"
WISHLIST_MAX_LEN = 50
VARIANCE = 10


class LazyLoadingPage(object):

    def __init__(self, steam_id=None, threshold=None, locale=None):
        self.steam_id = steam_id or STEAM_ID
        self.threshold = threshold or THRESHOLD
        self.locale = locale or LOCALE
        self._req = None
        self._soup = None

    @property
    def req(self):
        if self._req is None:
            self._req = requests.get(
                WISHLIST_URL.format(self.steam_id),
                params={"cc": self.locale, "sort": "price"})
        return self._req

    @property
    def soup(self):
        if self._soup is None:
            self._soup = BeautifulSoup(self.req.text, "html.parser")
        return self._soup

    def __str__(self):
        return "{cls} (url: {url})".format(
            cls=self.__class__.__name__,
            url=self.req.url)


class WishList(LazyLoadingPage):

    @property
    def apps(self):
        return (Apps(app) for app in self.soup.find_all('div', 'wishlistRow'))

    @property
    def matches(self):
        return True


class Apps(object):

    def __init__(self, soup):
        self.soup = soup

    @property
    def app_id(self):
        return self.soup['id'][5:]

    @property
    def title(self):
        return self.soup.h4.string

    @property
    def discount(self):
        return self.soup.select_one('div.discount_pct')

    @property
    def price_discounted(self):
        return self.soup.select_one('div.discount_final_price')

    @property
    def price_default(self):
        price_default = None
        try:
            price = self.soup.select_one('div.price')
            price_default = price.string.strip(' \t\n\r')
        finally:
            return price_default

if __name__ == "__main__":
    wl = WishList()
    for app in wl.apps:
        print(app.app_id, app.title, app.discount, app.price_discounted,
         app.price_default)
