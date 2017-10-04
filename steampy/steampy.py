# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup


THRESHOLD = 33
VARIANCE = 10
STEAM_ID = '76561197987677089'
LOCALE = 'ee'
STEAM_STORE_URL = "https://store.steampowered.com/app/{}"
WISH_LIST_URL = "https://steamcommunity.com/profiles/{}/wishlist"


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
                WISH_LIST_URL.format(self.steam_id),
                params={"cc": self.locale, "sort": "price"})
        return self._req

    @property
    def soup(self):
        if self._soup is None:
            self._soup = BeautifulSoup(self.req.text, "html.parser")
        return self._soup


class WishList(LazyLoadingPage):

    @property
    def apps(self):
        """Return compiled app info, truncate wishlist"""
        return (Apps(app) for app in self.soup.find_all('div', 'wishlistRow'))

    @property
    def length(self):
        """Return wishlist length"""
        return len(list(self.apps))

    @property
    def matches(self):
        """Return only matching titles"""
        return (app for app in self.apps if app.discount_int >= self.threshold)

    @property
    def close_matches(self):
        """Return close matched titles based on tolerance"""
        tolerance = range(self.threshold - VARIANCE, self.threshold)
        return (app for app in self.apps if app.discount_int in tolerance)

    @property
    def discounted(self):
        """Return only discounted titles"""
        return (app for app in self.apps if app.discount)

    def __str__(self):
        return "Steampy (url: {url})\n".format(url=self.req.url)


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
        discount = None
        try:
            discount_pct = self.soup.select_one('div.discount_pct')
            discount = discount_pct.string
        finally:
            return discount

    @property
    def discount_int(self):
        discount_int = None
        try:
            discount_int = int(self.discount.strip('%-'))
        finally:
            return discount_int

    @property
    def price_discounted(self):
        price_discounted = None
        try:
            discount_fp = self.soup.select_one('div.discount_final_price')
            price_discounted = discount_fp.string
        finally:
            return price_discounted

    @property
    def store_url(self):
        return STEAM_STORE_URL.format(self.app_id)

    @property
    def price_default(self):
        price_default = None
        try:
            price = self.soup.select_one('div.price')
            price_default = price.string.strip(' \t\n\r')
        finally:
            return price_default


def prepare_payload(wish_list, include_close_matches=True):
    template = (u"{0.title} is {0.price_discounted} with {0.discount} off:"
                u"\n{0.store_url}\n")
    payload = "".join(template.format(app) for app in wish_list.matches)

    if include_close_matches and list(wish_list.close_matches):
        payload += "You have some close matches:\n"
        payload += "".join(
            template.format(app) for app in wish_list.close_matches)
    return payload


if __name__ == "__main__":
    wl = WishList(STEAM_ID)
    print wl
    print prepare_payload(wl).encode('utf-8')


