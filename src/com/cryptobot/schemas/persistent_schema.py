import persistent
from com.cryptobot.schemas.schema import Schema


class PersistentSchema(Schema, persistent.Persistent):
    def __init__(self) -> None:
        super().__init__()
