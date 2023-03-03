# Scrapy settings for carparser project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'carparser'

SPIDER_MODULES = ['carparser.spiders']
NEWSPIDER_MODULE = 'carparser.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = ('Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:106.0)'
#               ' Gecko/20100101 Firefox/106.0')

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 7
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Host': 'www.avito.ru',   # playwright переписывает
    # для playwright user-agent лучше здесь тогда соблюдается порядок заголовков
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    # 'Upgrade-Insecure-Requests': '1',
    # 'Sec-Fetch-Dest': 'document',
    # 'Sec-Fetch-Mode': 'navigate',
    # 'Sec-Fetch-Site': 'cross-site',   # лучше 'none'
    # 'Sec-Fetch-User': '?1',
    # Optional Standard Headers:
    # #'Content-Type': 'application/json;charset=utf-8',
    # #'Referer': 'https://www.avito.ru/tyumen/avtomobili?cd=1&radius=75&s=104',
    # #'DNT': '1',
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'carparser.middlewares.CarparserSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'carparser.middlewares.CarparserDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'carparser.type_pipelines.TypeConversionPipeline': 200,
    'carparser.db_pipelines.DuckdbPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = False
# The initial download delay
AUTOTHROTTLE_START_DELAY = 8
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 20
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 600
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Minimum level to log. Available levels are: CRITICAL, ERROR, WARNING, INFO, DEBUG
LOG_LEVEL = 'INFO'

# new in version 2.7
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# zyte smartproxy headless proxy
HEADLESS_PROXY = 'localhost:3128'

# scrapy-playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_CONTEXTS = {
    'default': {
        'locale': DEFAULT_REQUEST_HEADERS['Accept-Language'],
        # устанавливает user-agent для playwright динамических запросов
        'user_agent': DEFAULT_REQUEST_HEADERS['User-Agent'],
        # 'proxy': {'server': HEADLESS_PROXY},
        # 'viewport': {'width': 1920, 'height': 1080},
    },
    # 'for_proxy': {
    #     'locale': DEFAULT_REQUEST_HEADERS['Accept-Language'],
    #     'user_agent': DEFAULT_REQUEST_HEADERS['User-Agent'],
    #     'proxy': {'server': HEADLESS_PROXY},
    # },
}
PLAYWRIGHT_BROWSER_TYPE = 'firefox'
PLAYWRIGHT_LAUNCH_OPTIONS = {'headless': True, 'timeout': 20 * 1000}

# Database
DB_NAME = '~/datadir/cars.duckdb'
BATCH_SIZE = 40
