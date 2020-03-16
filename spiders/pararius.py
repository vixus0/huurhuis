import os
import re
import sys
from apartment import Apartment
from datetime import datetime
from scrapy import Spider

def fixdate(date):
    try:
        return datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
    except ValueError:
        return date

class ParariusSpider(Spider):
    name = 'pararius'
    start_urls = [
            'https://www.pararius.com/apartments/amsterdam/0-3000/75m2/3-bedrooms'
            ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.exists('.pararius_delta'):
            self.previous_first_listing = open('.pararius_delta').read()
        else:
            self.previous_first_listing = None
        self.first_listing = True

    def parse(self, response):
        for details in response.css('.search-results-list .details'):
            listing_url = details.css('h2 > a::attr("href")').get()
            listing_url = response.urljoin(listing_url)

            if listing_url == self.previous_first_listing:
                self.logger.warn('Hit the first result of the previous run - STOPPING')
                return

            if self.first_listing:
                self.logger.debug('First listing: %s', listing_url)
                open('.pararius_delta', 'w').write(listing_url)
                self.first_listing = False

            yield response.follow(listing_url, self.parse_listing)

        next_page = response.css('.pagination > .next > a::attr("href")').get()

        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_listing(self, response):
        details = response.css('#details > dl')
        dts = details.css('dt::text').getall()
        dds = details.css('dd::text').getall()
        dl = { d[0]:d[1] for d in zip(dts, dds) }

        if dl['Offered since'] == '> 3 months':
            self.logger.info('Property more than 3 months old - SKIPPING')
            return

        under_contract = details.css('span.under-contract::text').get()

        if under_contract is not None:
            self.logger.info(f'Property taken: {under_contract} - SKIPPING')
            return

        desc = ''.join(response.css('#description p.text::text').getall()).lower()

        yield Apartment(
                site = self.name,
                street = dl['Street'],
                price = dl['Rent per month'],
                bedrooms = dl['Number of bedrooms'],
                surface = dl['Square meters'],
                url = response.url,
                available = fixdate(dl['Available from']),
                since = fixdate(dl['Offered since']),
                postcode = dl['Postal code'],
                description = desc,
                )
