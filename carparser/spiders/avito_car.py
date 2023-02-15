from datetime import datetime, timezone

from rfc3986 import builder
import scrapy
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings
from carparser.items import Car
from scrapy_playwright.page import PageMethod


def should_abort_request(request):  # Пропускаем ненужные запросы (ускорение парсинга)
    block_resource_types = [
        'beacon',
        'csp_report',
        'font',
        'image',
        'images',
        'imageset',
        'media',
        'object',
        'texttrack',
        #  we can even block stylsheets and scripts though it's not recommended:
        # 'stylesheet',
        # 'script',
        # 'xhr',
    ]
    block_resource_names = [
        '.jpg',
        'hybrid.ai',
        'buzzoola.com',
        'criteo.com',
        'vk.com',
        'mail.ru',
        'yandex.ru',
        # 'adzerk',
        'analytics',
        # 'cdn.api.twitter',
        'doubleclick',
        # 'exelator',
        # 'facebook',
        'fontawesome',
        'google',
        'google-analytics',
        'googletagmanager',
    ]
    if request.resource_type in block_resource_types:
        return True
    if any(key in request.url for key in block_resource_names):
        return True
    return False


class AvitoCarSpider(Spider):
    name = 'avito_car'
    custom_settings = {
        'PLAYWRIGHT_ABORT_REQUEST': should_abort_request,
        'PLAYWRIGHT_CONTEXTS': {
            'default': {
                'locale': get_project_settings().get('DEFAULT_REQUEST_HEADERS')['Accept-Language'],
                # устанавливает user-agent для playwright динамических запросов
                'user_agent': get_project_settings().get('DEFAULT_REQUEST_HEADERS')['User-Agent'],
                # 'viewport': {
                #     'width': 1920,
                #     'height': 1080,
                # },
            },
        },
    }
    allowed_domains = ['avito.ru']
    base_url = 'https://www.avito.ru'
    url_path = '/tyumen/avtomobili'
    params = {
        'cd': '1',
        # 'p': 1,     # Страница
        'radius': '75',
        's': '104',     # Сортировка по дате
        # 'user': '1',    # Частные
        'localPriority': '1',   # Сначала в выбранном радиусе
    }
    num_pages = 2
    next_page = 1
    car_count = 0
    # car_ids = set()

    def start_requests(self):
        # https://www.avito.ru/tyumen/avtomobili?cd=1&radius=75&s=104&localPriority=1
        url_builder = builder.URIBuilder.from_uri(self.base_url)
        url = url_builder.add_path(self.url_path).add_query_from(self.params).geturl()
        # headers = {'Referer': 'https://www.avito.ru/tyumen/avtomobili?cd=1&radius=75&s=104'}
        # headers.update({'User-Agent': self.settings.get('USER_AGENT')})

        yield scrapy.Request(url=url, callback=self.parse_list_cars, meta={
            'playwright': True,
            'playwright_include_page': True,
            'playwright_page_methods': [PageMethod('wait_for_selector', 'div[data-marker=item]')],
            'errback': self.errback,
        })

    async def parse_list_cars(self, response):
        resp_dt = datetime.now(timezone.utc).replace(microsecond=0)
        self.logger.debug(f'Request headers: {response.request.headers}')

        page = response.meta.get("playwright_page")
        if page:
            # screenshot = await page.screenshot(path="scrapy_pw.png", full_page=True)
            await page.close()

        self.logger.info(f'{resp_dt} Page {self.next_page}')
        for car_item in response.css('div[data-marker=item]'):
            car = Car()
            title = car_item.css('a[data-marker=item-title]').attrib['title'].split(',')
            item_params = car_item.css('div[data-marker=item-specific-params]::text').getall()

            car['brand_model'] = title[0].strip()
            if len(title) < 4:  # 'Новый '
                car['brand_model'] = car['brand_model'][6:]
                car['is_new_auto'] = 'True'
            car['year'] = title[1].strip()
            car['item_price'] = car_item.css('span[data-marker=item-price]>span::text').get().lstrip('от')
            car['item_price'] = ''.join(car['item_price'].split())
            car['url'] = car_item.css('a[data-marker=item-title]').attrib['href']
            car['site'] = self.base_url
            car['item_id'] = car_item.attrib['data-item-id']
            if len(item_params) > 0:
                if item_params[0] == ', ':  # битый
                    car['crash'] = 'True'
                    item_params.pop(0)
                item_params = item_params[0].split(',')
                if len(item_params) > 4:    # не новый
                    car['mileage'] = item_params.pop(0).rstrip('км')
                    car['mileage'] = ''.join(car['mileage'].split())
                else:
                    car['mileage'] = '0'
                car['engine_type'] = item_params[-1].strip()
                capacity, engine_hp = item_params[0].split('(')
                engine_hp = engine_hp.rstrip('лс.)')
                car['engine_hp'] = ''.join(engine_hp.split())
                cap_transm = capacity.strip().split()
                if len(cap_transm) > 1:
                    car['capacity'] = cap_transm[0].strip()
                    car['transmission'] = cap_transm[1].strip()
                elif len(cap_transm) == 1:
                    car['capacity'] = '0.0'     # Электро двигатель
                    car['transmission'] = cap_transm[0].strip()
                car['parse_time'] = resp_dt

            self.car_count += 1
            self.logger.info(f"{self.car_count:>5} {car['brand_model']}, {car['year']}")
            yield car

        url_builder = builder.URIBuilder.from_uri(self.base_url)
        if self.next_page < self.num_pages:
            self.next_page += 1
            params = {
                'cd': '1',
                'p': self.next_page,
                'radius': '75',
                's': '104',
                'localPriority': '1',
            }
            next_page_url = url_builder.add_path(self.url_path).add_query_from(params).geturl()
            yield scrapy.Request(url=next_page_url, callback=self.parse_list_cars, meta={
                'playwright': True,
                'playwright_include_page': True,
                'playwright_page_methods': [PageMethod('wait_for_selector', 'div[data-marker=item]')],
                'errback': self.errback,
            })

    async def errback(self, failure):
        self.logger.error(repr(failure))
        page = failure.request.meta["playwright_page"]
        await page.close()
