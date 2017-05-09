# -*- coding: utf-8 -*-
import re
import os
import requests
from bs4 import BeautifulSoup


THRESHOLD = 50
STEAM_ID = '76561197987677089'
LOCALE = 'gb'

STEAM_STORE_URL = "https://store.steampowered.com/app/"
WISHLIST_URL = "http://steamcommunity.com/profiles/{}/wishlist"
NEXMO_SMS_URL = "https://rest.nexmo.com/sms/json"
WISHLIST_MAX_LEN = 50
VARIANCE = 10


class Steampy():

    def __init__(self, steam_id=None, threshold=None, locale=None):
        self.steam_id = steam_id or STEAM_ID
        self.threshold = threshold or THRESHOLD
        self.locale = locale or LOCALE

    def get_content(self):
        response = requests.get(
            WISHLIST_URL.format(self.steam_id),
            params={"cc": LOCALE, "sort": "price"})

        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.find_all('div', 'wishlistRow'):
            app_id = row['id'][5:]
            yield {
                'app_id': app_id,
                'store_url': ''.join([STEAM_STORE_URL, app_id]),
                'title': row.h4.string,
                'discount': ''.join([discount.string for discount in row.select('div.discount_pct')]),
                'price_discounted': ''.join([d_price.string for d_price in row.select('div.discount_final_price')]),
                'price_default': ''.join([price.string.strip(' \t\n\r') for price in row.select('div.price')]),
            }

    def truncate_wish_list(self, item_list):
        print item_list
        initial_item_list = list(item_list)
        short_item_list = initial_item_list
        if len(item_list) > WISHLIST_MAX_LEN and WISHLIST_MAX_LEN > 0:
            print "[!] Warning, wishlist exceeds {} (actual {})".format(
                WISHLIST_MAX_LEN, len(item_list))

            short_item_list = initial_item_list[:WISHLIST_MAX_LEN]
            truncated_items = initial_item_list[WISHLIST_MAX_LEN:]
            print "List truncated to {}, lost {}: {}".format(
                len(short_item_list),
                len(truncated_items),
                [app['app_id'] for app in truncated_items])
        return short_item_list

    def prepare_payload(self, item_list, include_close_matches=True):
        matches, close_matches = [], []
        # print len(item_list)
        for app in item_list:
            if app["discount"]:
                discount = int(re.sub("[^0-9]", "", app["discount"]))
                template = u"{title} is {price_discounted} with {discount} off:\n{store_url}\n".format(**app)
                if discount >= THRESHOLD:
                    matches.append(template)
                if include_close_matches:
                    if THRESHOLD - discount <= VARIANCE and not discount >= THRESHOLD and discount > 0:
                        close_matches.append(template)
        payload = "\n".join(matches)
        if close_matches:
            payload += "You have some close matches:\n" + '\n'.join(
                close_matches) if close_matches else ''
        return payload

    def send_message(self, payload, recepient_number):
        response = requests.get(NEXMO_SMS_URL, params={
            'api_key': os.environ.get('NEXMO_API_KEY'),
            'api_secret': os.environ.get('NEXMO_API_SECRET'),
            'to': recepient_number,
            'from': "Steampy",
            'text': payload})
        response_data = response.json()

        print response_data
        print "Sent to {0}, n/o messages {1}: {2}".format(
            recepient_number,
            response_data["message-count"],
            ', '.join([m["message-id"] for m in response_data["messages"]]))
        return response_data

    def main(self):
        item_list = self.get_content()
        short_list = self.truncate_wish_list(list(item_list))
        payload = self.prepare_payload(short_list)
        print [payload]

if __name__ == "__main__":
    s = Steampy()
    s.main()
