import importlib
import os
import datetime


def get_class_by_fullname(fullname: str):
    class_name = fullname.split('.')[-1]
    module = '.'.join(fullname.split('.')[0:-1])
    module = importlib.import_module(module)
    cls = getattr(module, class_name)

    return cls


def modification_date(filename):
    t = os.path.getmtime(filename)

    return datetime.datetime.fromtimestamp(t)
