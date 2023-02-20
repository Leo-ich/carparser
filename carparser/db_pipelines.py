# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import duckdb

logger = logging.getLogger(__name__)


class DuckdbPipeline:

    def __init__(self):
        # перегружается настройками !
        self.db_name = 'test_db.duckdb'
        self.batch_size = 1

        self.connection = None
        self.item_id_set = set()

    def create_table(self):
        q = """
            CREATE TABLE IF NOT EXISTS cars_raw
            (
                item_id     BIGINT  PRIMARY KEY,
                brand_model VARCHAR NOT NULL,
                item_price  BIGINT  NOT NULL,
                capacity    DECIMAL,
                engine_hp   INT,
                mileage     INT,
                year        INT,
                engine_type VARCHAR,
                transmission VARCHAR,
                is_new_auto BOOLEAN,
                crash       BOOLEAN,
                site        VARCHAR,
                url         VARCHAR,
                time        TIMESTAMPTZ,
                parse_time  TIMESTAMPTZ
            )
            """
        self.connection.execute(q).commit()

    def db_connect(self):
        connection = duckdb.connect(self.db_name)
        return connection

    def open_spider(self, spider):
        self.db_name = spider.settings.get('DB_NAME', None) or self.db_name
        self.batch_size = spider.settings.get(
            'BATCH_SIZE', None) or self.batch_size
        self.connection = self.db_connect()
        self.create_table()
        self.connection.begin()

    def write_item(self, item):
        try:
            self.connection.execute(
                f"INSERT OR IGNORE INTO cars_raw ({', '.join(item.keys())})"
                f" VALUES ({', '.join('?'*len(item))});",
                item.values()
            )
        except Exception as error:
            logger.exception(error)
            self.connection.rollback()
            self.connection.begin()
            raise

    def process_item(self, item, spider):
        if item['item_id'] not in self.item_id_set:
            self.write_item(item)
        self.item_id_set.add(item['item_id'])
        if len(self.item_id_set) >= self.batch_size:
            self.connection.commit()
            self.item_id_set = set()
            self.connection.begin()
        return item

    def close_spider(self, spider):
        if len(self.item_id_set) > 0:
            self.connection.commit()
            self.item_id_set = set()
        # print(self.connection.sql('DESCRIBE cars').show())
        print(self.connection.sql('SELECT * FROM cars_raw').show())
        if self.connection:
            self.connection.close()
        logger.debug('Close db')
