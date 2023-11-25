import re

from web_poet import WebPage, SelectorExtractor, field
from carparser.items import Car


class CarListPage(WebPage):

    def car_list(self):
        return self.css('*[data-marker=item]')


class CarExtractor(SelectorExtractor[Car]):
    pattern = re.compile(r'(?:\d\.\d)?\s(AT|CVT|AMT|MT)\s')

    def __init__(self, *args, page_data: dict = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_data = page_data or dict()
        self.title = self.css(
            '*[data-marker=item-title]').attrib['title'].split(',')
        self.item_params = self.css(
            '*[data-marker=item-specific-params]::text').getall()
        if len(self.item_params) > 1:
            self.item_params = self.item_params[1].split(',')
        elif len(self.item_params) > 0:
            self.item_params = self.item_params[0].split(',')

    @staticmethod
    def remove_spaces(string: str) -> str:
        return ''.join(string.split())

    @field
    def item_id(self):
        return self.css('*').attrib['data-item-id']

    @field
    def brand_model(self):
        result = re.sub(
            r'( [0-9]\.[0-9].*)* (AT|CVT|AMT|MT)$', '', self.title[0].strip()
        )
        if self.is_new_auto == 'True':
            return result[6:]
        return result

    @field
    def item_price(self):
        result = self.css(
            '*[data-marker=item-price]>strong>span::text').get().lstrip('от')
        return self.remove_spaces(result)

    @field
    def capacity(self):     # объём мотора
        data = [d for d in self.item_params if re.search(self.pattern, d)]
        if data:
            result = data[0].split('(')[0].strip().split()
            if len(result) > 1:
                return result[0].strip()
        return '0.0'

    @field
    def engine_hp(self):
        data = [d for d in self.item_params if 'л.с.)' in d]
        if data:
            result = data[0].split('(')[1].rstrip('лс.)')
            return self.remove_spaces(result)
        return '0'

    @field
    def mileage(self):
        data = [d for d in self.item_params if re.search(r'[0-9]+\sкм', d)]
        if data:
            result = data[0].rstrip('км')
            return self.remove_spaces(result)
        return '0'

    @field
    def year(self):
        return self.title[1].strip()

    @field
    def engine_type(self):
        if len(self.item_params) > 0:
            return self.item_params[-1].strip()
        return ''

    @field
    def transmission(self):
        data = [d for d in self.item_params if re.search(self.pattern, d)]
        if data:
            result = re.search(self.pattern, data[0])
            return result[1].strip()
        return ''

    @field
    def is_new_auto(self):
        if len(self.title) < 4:
            return 'True'
        return 'False'

    @field
    def crash(self):
        if len(self.css(
                '*[data-marker=item-specific-params]::text').getall()) > 1:  # битый
            return 'True'
        return 'False'

    @field
    def site(self):
        return self.page_data.get('base_url')

    @field
    def url(self):
        return self.css('*[data-marker=item-title]').attrib['href']

    @field
    def time(self):
        return None

    @field
    def parse_time(self):
        return self.page_data.get('parse_dt')
