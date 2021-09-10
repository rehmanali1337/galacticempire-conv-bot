import shelve
import os
DB_LOCATION = 'Cache'


class DictCache:
    def __init__(self, db_name):
        if not os.path.exists(DB_LOCATION):
            os.makedirs(DB_LOCATION)
        self.db_file = f'{DB_LOCATION}/{db_name}'

    def add_item(self, key: str = None, value: str = None):
        key = str(key)
        with shelve.open(self.db_file, writeback=True) as db:
            db[key] = value

    def get_item(self, key):
        key = str(key)
        with shelve.open(self.db_file, writeback=True) as db:
            return db[key]

    def remove_item(self, key):
        key = str(key)
        with shelve.open(self.db_file, writeback=True) as db:
            db.pop(key)

    def key_exists(self, key):
        key = str(key)
        with shelve.open(self.db_file, writeback=True) as db:
            return key in db.keys()

    def get_all_keys(self):
        with shelve.open(self.db_file, writeback=True) as db:
            return db.keys().copy()

    def get_all_values(self):
        with shelve.open(self.db_file, writeback=True) as db:
            return list(db.values())


class ListCache(DictCache):
    def __init__(self, db_name):
        super().__init__(db_name)
        self.list_key = 'list_of_items'
        with shelve.open(self.db_file, writeback=True) as d:
            if self.list_key not in d.keys():
                d[self.list_key] = []

    def item_exists(self, item):
        with shelve.open(self.db_file, writeback=True) as d:
            return item in d[self.list_key]

    def add_item(self, item):
        with shelve.open(self.db_file, writeback=True) as d:
            d[self.list_key].append(item)
            d.sync()

    def get_all(self):
        with shelve.open(self.db_file, writeback=True) as d:
            return d[self.list_key]

    def remove_item(self, item):
        with shelve.open(self.db_file, writeback=True) as d:
            try:
                d[self.list_key].remove(item)
                d.sync()
            except ValueError:
                return
