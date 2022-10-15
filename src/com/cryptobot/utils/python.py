import importlib


def get_class_by_fullname(fullname: str):
    class_name = fullname.split('.')[-1]
    module = '.'.join(fullname.split('.')[0:-1])
    module = importlib.import_module(module)
    cls = getattr(module, class_name)

    return cls
