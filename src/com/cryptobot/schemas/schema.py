import json


class Schema(object):
    def __init__(self) -> None:
        super(Schema).__new__()

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else (
            o._asdict() if hasattr(o, '_asdict') else None
        ),
            sort_keys=True, indent=4)
