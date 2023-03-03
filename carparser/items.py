# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class Car(Item):

    item_id = Field()
    brand_model = Field()
    item_price = Field()
    capacity = Field()
    engine_hp = Field()
    mileage = Field()
    year = Field()
    engine_type = Field()
    transmission = Field()
    is_new_auto = Field()
    crash = Field()
    site = Field()
    url = Field()
    time = Field()
    parse_time = Field()
