import ZODB
import ZODB.FileStorage

storage = ZODB.FileStorage.FileStorage('trading-bot.fs')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root


def get_storage():
    return storage


def get_db():
    return db


def get_connection():
    return connection


def get_root():
    return root


class ZODBRunnable():
    def __init__(self) -> None:
        self.storage = get_storage()
        self.db = get_db()
        self.connection = get_connection()
        self.root = get_root()
