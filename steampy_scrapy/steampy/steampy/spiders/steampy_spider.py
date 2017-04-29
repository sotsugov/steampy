# -*- coding: utf-8 -*-
import scrapy

STEAM_STORE_URL = "https://store.steampowered.com/app/"
WISHLIST_URL = 'https://steamcommunity.com/profiles/{}/wishlist?cc={}'


class SteampySpider(scrapy.Spider):
    name = "steampy"

    def start_requests(self):
        yield scrapy.Request(WISHLIST_URL.format(self.profile, self.locale))

    def parse(self, response):
        # extract the wishlist items
        for row in response.css('div.wishlistRow'):
            app_id = row.css('::attr(id)').extract_first()[5:]
            price_default = row.css('div.price::text').extract_first()
            yield {
                'app_id': app_id,
                'store_url': ''.join([STEAM_STORE_URL, app_id]),
                'title': row.css('h4.ellipsis::text').extract_first(),
                'discount': row.css('div.discount_pct::text').extract_first(),
                'price_discounted': row.css('div.discount_final_price::text').extract_first(),
                'price_default': unicode(price_default).strip(' \t\n\r'),
            }
