# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import copy
from scrapy.item import Item, Field
from peewee import Model, SqliteDatabase, TextField

db = SqliteDatabase('cars.db')


class PeeWeeItem(Item):

    def __init__(self, model):
        super(self.__class__, self).__init__()
        self._model = model
        for key in model._meta.fields.keys():
            self.fields[key] = Field()

    def __setitem__(self, key, value):
        if key not in self.fields:
            self.fields[key] = Field()
        self._values[key] = value

    def copy(self):
        return copy.deepcopy(self)

    @property
    def model(self):
        return self._model


class Car(Model):

    itemID = TextField()
    itemPrice = TextField()
    withDelivery = TextField()
    vehicle_type = TextField()
    type_of_trade = TextField()
    capacity = TextField()
    color = TextField()
    wheel = TextField()
    engine = TextField()
    brand = TextField()
    model = TextField()
    condition = TextField()
    vladeltsev_po_pts = TextField()
    mileage = TextField()
    year = TextField()
    body_type = TextField()
    kolichestvo_dverey = TextField()
    generation = TextField()
    engine_type = TextField()
    drive = TextField()
    transmission = TextField()
    modification = TextField()
    complectation = TextField()
    isPersonalAuto = TextField()
    isNewAuto = TextField()
    userAuth = TextField()
    isShop = TextField()
    isASDClient = TextField()
    vertical = TextField()
    categoryId = TextField()
    categorySlug = TextField()
    microCategoryId = TextField()
    locationId = TextField()

    usilitel_rulya = TextField()
    elektrosteklopodemniki = TextField()
    upravlenie_klimatom = TextField()
    salon = TextField()

    price_metric = TextField()
    url = TextField()
    coords = TextField()
    address = TextField()
    time = TextField()
    description = TextField()
    stats = TextField()
    autoteka_teaser = TextField()
    car_market_price = TextField()

    class Meta:
        database = db
