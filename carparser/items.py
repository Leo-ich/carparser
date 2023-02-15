# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class Car(Item):

    item_id = Field()
    brand_model = Field()
    item_price = Field()
#     withDelivery = TextField()
#     vehicle_type = TextField()
#     type_of_trade = TextField()
    capacity = Field()
#     color = TextField()
#     wheel = TextField()
    engine_hp = Field()
#     brand = Field()
#     model = Field()
#     condition = TextField()
#     vladeltsev_po_pts = TextField()
    mileage = Field()
    year = Field()
#     body_type = TextField()
#     kolichestvo_dverey = TextField()
#     generation = TextField()
    engine_type = Field()
#     drive = TextField()
    transmission = Field()
#     modification = TextField()
#     complectation = TextField()
#     isPersonalAuto = TextField()
    is_new_auto = Field()
    crash = Field()
#     userAuth = TextField()
#     isShop = TextField()
#     isASDClient = TextField()
#     vertical = TextField()
#     categoryId = TextField()
#     categorySlug = TextField()
#     microCategoryId = TextField()
#     locationId = TextField()
#
#     usilitel_rulya = TextField()
#     elektrosteklopodemniki = TextField()
#     upravlenie_klimatom = TextField()
#     salon = TextField()
#
#     price_metric = TextField()
    site = Field()
    url = Field()
#     coords = TextField()
#     address = TextField()
    time = Field()
    parse_time = Field()
#     description = TextField()
#     stats = TextField()
#     autoteka_teaser = TextField()
#     car_market_price = TextField()
#
#     class Meta:
#         database = db
