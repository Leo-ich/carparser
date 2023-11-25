from datetime import datetime, timezone

from rfc3986 import builder
import scrapy
from scrapy.spiders import Spider
from scrapy_playwright.page import PageMethod
# from scrapy.utils.trackref import print_live_refs

from carparser.pages import CarListPage, CarExtractor


# Пропускаем ненужные запросы (ускорение парсинга)
def should_abort_request(request):
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
    ]
    block_resource_names = [
        '.jpg',
        'hybrid.ai',
        'buzzoola.com',
        'criteo.com',
        'vk.com',
        'mail.ru',
        'yandex.ru',
        'analytics',
        'doubleclick',
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
    num_pages = 30
    next_page = 1
    car_count = 0
    parse_dt = datetime.now(timezone.utc).replace(microsecond=0)
    allowed_domains = ['avito.ru']
    base_url = 'https://www.avito.ru'
    url_path = '/tyumen/avtomobili'
    params = {
        'cd': '1',
        'radius': '75',
        's': '104',             # Сортировка по дате
        'localPriority': '1',   # Сначала в выбранном радиусе
    }
    custom_settings = {
        'PLAYWRIGHT_ABORT_REQUEST': should_abort_request,
    }

    def start_requests(self):
        # https://www.avito.ru/tyumen/avtomobili?cd=1&radius=75&s=104&localPriority=1
        url_builder = builder.URIBuilder.from_uri(self.base_url)
        url = url_builder.add_path(
            self.url_path).add_query_from(self.params).geturl()

        yield scrapy.Request(url=url, callback=self.parse_list_cars, meta={
            'playwright': True,
            'playwright_include_page': True,
            'playwright_page_methods': [PageMethod(
                'wait_for_selector', 'div[data-marker=item]', timeout=20000)],
            'errback': self.errback,
        })

    async def parse_list_cars(self, response, web_page: CarListPage):
        self.logger.debug(f'Request headers: {response.request.headers}')

        page = response.meta.get("playwright_page")
        if page:
            # screenshot = await page.screenshot(path="scrapy_pw.png",
            #                                    full_page=True)
            await page.close()

        self.logger.info(f'Page {self.next_page}')
        for item in web_page.car_list():
            try:
                car = await CarExtractor(
                    item,
                    page_data={'base_url': self.base_url,
                               'parse_dt': self.parse_dt}
                ).to_item()
            except Exception as e:
                self.car_count += 1
                self.logger.exception(e)
                continue
            self.car_count += 1
            self.logger.debug(
                f"{self.car_count:>5} {car['brand_model']}, {car['year']}"
            )
            yield car

        url_builder = builder.URIBuilder.from_uri(self.base_url)
        if self.next_page < self.num_pages:
            self.next_page += 1
            params = self.params.copy()
            params['p'] = str(self.next_page)
            next_page_url = url_builder.add_path(
                self.url_path).add_query_from(params).geturl()
            yield scrapy.Request(
                url=next_page_url, callback=self.parse_list_cars, meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [PageMethod(
                        'wait_for_selector', 'div[data-marker=item]', timeout=20000)],
                    'errback': self.errback,
                }
            )
        # self.logger.info(print_live_refs(AvitoCarSpider))

    async def errback(self, failure):
        self.logger.error(repr(failure))
        page = failure.request.meta['playwright_page']
        if page:
            ts = datetime.now(timezone.utc).replace(microsecond=0).timestamp()
            scr_name = f"~/datadir/scrapy_pw_{ts}.png"
            await page.screenshot(path=scr_name, full_page=True)
            await page.close()
