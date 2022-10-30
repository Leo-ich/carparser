import json
from time import time

from rfc3986 import builder
import scrapy
from scrapy.spiders import Spider
from carparser.items import Car, PeeWeeItem

# GET 'https://m.avito.ru/api/17/items/2203163445?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir&action=view&context=H4sIAAAAAAAA_0q0MrSqLrYytFKqULIutjI2tFJKzC02Ki-xTM41S85PTzJNr0g3yDetSE4sMzPNsrAoU7KuBQQAAP__y81gsTUAAAA'
# Referer: https://m.avito.ru/tyumen/avtomobili/toyota_camry_2001_2203163445

class AvitoCarSpider(Spider):
    name = 'avito_car'
    allowed_domains = ['avito.ru']
    base_url = 'https://m.avito.ru/api/11/items'
    params = {
        'key': 'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir',
        'categoryId': 9,    # auto
        'locationId': 659020,  # Tyumen
        'searchRadius': 200,
        'radius': 200,
        'page': 1,
        'lastStamp': int(time() - 60),
        'display': 'list',
        'limit': 30,
        'pageId': 'H4sIAAAAAAAA_0q0MrSqLrYyNLRSKskvScyJT8svzUtRss60MjQyMLa0rgUEAAD__1977c8hAAAA',
    }
    base_car_url = 'https://m.avito.ru/api/17/items'
    car_params = {
        'key': params['key'],
        'action': 'view',
        'context': params['pageId'],
    }
    car_count = 0
    car_ids = set()

    @staticmethod
    def add_url_params(url, params):
        url_builder = builder.URIBuilder.from_uri(url)
        return url_builder.add_query_from(params).geturl()

    @staticmethod
    def add_url_path(url, path):
        url_builder = builder.URIBuilder.from_uri(url)
        return url_builder.add_path(path).geturl()

    def start_requests(self):
        # https://m.avito.ru/api/11/items?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir&categoryId=9&locationId=659020&searchRadius=200&radius=200&page=2&lastStamp=1624356240&display=list&limit=30&pageId=H4sIAAAAAAAA_0q0MrSqLrYyNLRSKskvScyJT8svzUtRss60MjS0tDS1rgUEAAD__4ByziIhAAAA
        url = self.add_url_params(self.base_url, self.params)
        headers = {'Referer': 'https://m.avito.ru/tyumen/avtomobili?cd=1&radius=200'}
        yield scrapy.Request(url=url, callback=self.parse_list_cars, headers=headers)

    def parse_list_cars(self, response):
        # print(response.request.headers)
        # print(response.headers)
        # print(response.text)
        result = json.loads(response.text)
        if result['status'] == 'ok':
            result = result['result']
        else:
            self.logger.error('car list parsing error')
            return
        count = result['count']
        last_stamp = result['lastStamp']
        next_page_id = result.get('nextPageId', None)

        cars = [i for i in result['items'] if i['type'] in ('item', 'xlItem')]  # or 'xlItem'
        for car in cars:
            self.car_count += 1
            car_id = car['value']['id']
            self.car_ids.add(car_id)
            car_url = self.add_url_path(self.base_url, f'/api/17/items/{car_id}')
            car_url = self.add_url_params(car_url, self.car_params)
            car_referer = car['value']['uri_mweb']
            car_headers = {'Referer': self.add_url_path(self.base_url, car_referer)}
            yield scrapy.Request(url=car_url, callback=self.parse_cars, headers=car_headers)
            # yield {'car_url': car_headers['Referer'], 'car_count': self.car_count, 'count': count, 'len_ids': len(self.car_ids)}

        if self.params['page'] < 2:
        # if next_page_id:
            self.params['page'] += 1
            self.params['pageId'] = next_page_id
            next_page_url = self.add_url_params(self.base_url, self.params)
            headers = {'Referer': 'https://m.avito.ru/tyumen/avtomobili?cd=1&radius=200'}
            yield scrapy.Request(url=next_page_url, callback=self.parse_list_cars, headers=headers)

    def parse_cars(self, response):
        result = json.loads(response.text)
        item = result['firebaseParams']
        item['price_metric'] = result['price']['metric']
        item['url'] = result['sharing']['url']
        item['coords'] = result['coords']
        item['address'] = result['address']
        item['time'] = result['time']
        item['description'] = result['description']
        item['stats'] = result.get('stats', {})
        item['autoteka_teaser'] = result.get('autotekaTeaser', {})
        item['car_market_price'] = result.get('carMarketPrice', {})
        return PeeWeeItem(Car(item))
