import importlib
import os
import datetime
import inspect
from typing import get_type_hints


def get_class_by_fullname(fullname: str):
    class_name = fullname.split('.')[-1]
    module = '.'.join(fullname.split('.')[0:-1])
    module = importlib.import_module(module)
    cls = getattr(module, class_name)

    return cls


def modification_date(filename):
    t = os.path.getmtime(filename)

    return datetime.datetime.fromtimestamp(t)


def execute_method_in_classes(method_name, folder, argument):
    results = []

    # loop through each file in the folder
    for file in os.listdir(folder):
        # check if the file is a Python file
        if file.endswith('.py'):
            # import the module and loop through the classes
            module_name = file[:-3]
            module = importlib.import_module(module_name, folder)
            for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
                # find the method in the class and execute it if found
                if hasattr(class_obj, method_name):
                    method = getattr(class_obj(), method_name)
                    results.append(method(argument))

    return results


def get_class_attributes(module) -> dict:
    class_attributes = {}
    # Iterate over the attributes of the module
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        # Check if the attribute is a class
        if isinstance(attribute, type):
            # Get the types of the attributes of the class
            type_hints = get_type_hints(attribute)
            # Add the name and attributes of the class to the dictionary
            class_attributes[attribute.__name__] = type_hints

    return class_attributes


def combine_lists(listA, listB):
    shared_items = list(set(listA) & set(listB))
    itemsA = list(set(listA) - set(listB))
    itemsB = list(set(listB) - set(listA))

    return shared_items + itemsA + itemsB
