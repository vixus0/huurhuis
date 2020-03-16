from scrapy import Item, Field

class Apartment(Item):
    site = Field()
    street = Field()
    price = Field()
    bedrooms = Field()
    surface = Field()
    url = Field()
    available = Field()
    since = Field()
    postcode = Field()
    description = Field()
