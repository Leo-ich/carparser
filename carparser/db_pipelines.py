# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from pathlib import Path
import duckdb

logger = logging.getLogger(__name__)


class DuckdbPipeline:

    def __init__(self):
        # перегружается настройками !
        self.db_name = ':memory:'
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
                parse_time  TIMESTAMPTZ,
                end_time    TIMESTAMPTZ,
                last_update TIMESTAMPTZ
            )
            """
        self.connection.execute(q).commit()

    def db_connect(self):
        connection = duckdb.connect(self.db_name)
        return connection

    def open_spider(self, spider):
        self.db_name = spider.settings.get('DB_NAME', None) or self.db_name
        if self.db_name != ':memory:':
            path = Path(self.db_name).expanduser().resolve()
            path.parent.mkdir(exist_ok=True, parents=True)
            self.db_name = str(path)
        self.batch_size = spider.settings.get(
            'BATCH_SIZE', None) or self.batch_size
        self.connection = self.db_connect()
        self.create_table()
        self.connection.begin()

    def execute_query(self, query, params):
        try:
            self.connection.execute(query, params)
        except Exception as error:
            logger.exception(error)
            self.connection.rollback()
            self.connection.begin()
            raise

    def write_item(self, item):
        query = (
            f"INSERT OR IGNORE INTO cars_raw ({', '.join(item.keys())})"
            f" VALUES ({', '.join('?'*len(item))});"
        )
        self.execute_query(query, item.values())

    def update_last_dt(self, item):
        query = """
           UPDATE cars_raw
           SET last_update=?, end_time=NULL
           WHERE item_id=?
        """
        self.execute_query(query, (item['parse_time'], item['item_id']))

    def update_end_dt(self, end_time):
        try:
            self.connection.execute("""
               UPDATE cars_raw
               SET end_time=$1
               WHERE end_time is NULL and last_update<$1
            """, (end_time,))
        except Exception as error:
            logger.exception(error)
            self.connection.rollback()
            raise

    def process_item(self, item, spider):
        if item['item_id'] not in self.item_id_set:
            self.write_item(item)
            self.update_last_dt(item)
        self.item_id_set.add(item['item_id'])
        if len(self.item_id_set) >= self.batch_size:
            self.connection.commit()
            self.item_id_set = set()
            self.connection.begin()
        return item

    def close_spider(self, spider):
        self.connection.commit()
        self.update_end_dt(str(spider.parse_dt))
        if len(self.item_id_set) > 0:
            self.item_id_set = set()
        # print(self.connection.sql('DESCRIBE cars').show())
        print(self.connection.sql('SELECT * FROM cars_raw').show())
        self.connection.close()
        logger.debug('Close db')
