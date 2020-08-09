import os
import pymongo


class _AppState:
    STATE = None

    def __init__(self):
        if not _AppState.STATE:
            _AppState.STATE = self
            self.db = _AppState.STATE._init_db()

    def __getattr__(self, item):
        return getattr(self.STATE, item)

    def _init_db(self):
        user = os.environ.get("db_user")
        db_pass = os.environ.get("db_password")
        database_url = os.environ.get('database_url')
        database_name = os.environ.get("database_name")
        client = pymongo.MongoClient(f"mongodb://{user}:{db_pass}@{database_url}/{database_name}?retryWrites=false")
        return client[database_name]


_AppState()


def get_db():
    return _AppState.STATE.db


