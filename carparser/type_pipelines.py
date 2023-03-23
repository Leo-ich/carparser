# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from rfc3986 import builder


class TypeConversionPipeline:

    def process_item(self, item, spider):
        item['item_id'] = self.__to_int(item['item_id'])
        item['brand_model'] = item.get('brand_model', '')
        item['item_price'] = self.__to_int(item['item_price'])
        item['capacity'] = self.__to_float(item.get('capacity', '0.0'))
        item['engine_hp'] = self.__to_int(item.get('engine_hp', '0'))
        item['mileage'] = self.__to_int(item.get('mileage', '0'))
        item['year'] = self.__to_int(item['year'])
        item['engine_type'] = item.get('engine_type', '')
        item['transmission'] = item.get('transmission', '')
        item['is_new_auto'] = self.__strtobool(item.get('is_new_auto', False))
        item['crash'] = self.__strtobool(item.get('crash', False))
        item['site'] = item.get('site', '')
        item['url'] = self.__to_absolute_url(item['site'], item.get('url', ''))
        item['time'] = str(item.get('parse_time'))
        item['parse_time'] = str(item.get('parse_time'))
        return item

    def __to_int(self, value):
        try:
            value = int(value)
        except ValueError:
            value = 0
        return value

    def __to_float(self, value):
        try:
            value = float(value)
        except ValueError:
            value = 0.0
        return value

    def __strtobool(self, value):
        if value == 'True':
            return True
        return False

    def __to_absolute_url(self, base_url, link):
        if not base_url or not link:
            return ''
        url_builder = builder.URIBuilder.from_uri(base_url)
        return url_builder.add_path(link).geturl()
