import os
import re
import sys
from apartment import Apartment
from datetime import datetime
from scrapy import Spider
from urllib.parse import urlparse

def fixdate(date):
    try:
        return datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
    except ValueError:
        return date

class FundaSpider(Spider):
    name = 'funda'
    start_urls = [
            'https://www.funda.nl/en/huur/amsterdam/0-3000/75+woonopp/onbepaalde-tijd/3+slaapkamers/sorteer-datum-af/'
            ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.exists('.funda_delta'):
            self.previous_first_listing = open('.funda_delta').read()
        else:
            self.previous_first_listing = None
        self.first_listing = True

    def parse(self, response):
        for details in response.css('ol.search-results .search-result-content-inner'):
            listing_url = details.css('.search-result__header-title-col > a::attr("href")').get()
            listing_url = urlparse(listing_url).path
            listing_url = response.urljoin(listing_url)

            if self.first_listing:
                self.logger.debug('First listing: %s', listing_url)
                self.logger.debug('Prev  listing: %s', self.previous_first_listing)
                if listing_url == self.previous_first_listing:
                    self.logger.warn('No new properties since last scrape - STOPPING')
                    return
                open('.funda_delta', 'w').write(listing_url)
                self.first_listing = False

            yield response.follow(listing_url, self.parse_listing)

        next_page = response.xpath('//a[@rel="next"]').attrib("href")

        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_listing(self, response):
        dl = {}

        for details in response.css('.object-kenmerken-body dl'):
            dts = details.css('dt::text').getall()
            dds = details.css('dd::text').getall()
            dl.update({ d[0]:d[1] for d in zip(dts, dds) })

        desc = ''.join(response.css('div.object-description-body::text').getall()).lower()

        yield Apartment(
                site = self.name,
                street = response.css('.object-header__title::text').get(),
                price = dl['Rent per month'],
                bedrooms = dl['Number of bedrooms'],
                surface = dl['Square meters'],
                url = response.url,
                available = fixdate(dl['Available from']),
                since = fixdate(dl['Offered since']),
                postcode = response.css('.object-header__subtitle::text').get().replace(' Amsterdam', ''),
                description = desc,
                )
