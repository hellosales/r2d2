# -*- coding: utf-8 -*-
'''
Helper functions for class names
'''


def class_for_name(name):
    """
    Returns a class for the string representation of the fully qualified class name
    """
    import importlib
    parts = name.split('.')
    module_name = ".".join(parts[:-1])

    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)

    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, parts[-1])
    return c


def name_for_class(obj):
    """
    Returns a string representation of the fully qualified class name
    """
#    return obj.__module__ + "." + obj.__class__.__name__
    return obj.__module__ + "." + obj.__name__
