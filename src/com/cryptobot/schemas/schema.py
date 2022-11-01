import json


class Schema:
    def __eq__(self, __o: object) -> bool:
        return (isinstance(__o, type(self)) and self.__key__ == __o.__key__)

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else (
            o._asdict() if hasattr(o, '_asdict') else None
        ),
            sort_keys=True, indent=4)
