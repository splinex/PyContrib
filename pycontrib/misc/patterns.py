#!/usr/bin/python3

"""Utile patterns."""


class Singleton(object):

    _instance = None
    _inited = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kw):
        if self._inited:
            return
        self.initialize(*args, **kw)
        self.__class__._inited = True

    def initialize(self, *args, **kw):
        pass

    @classmethod
    def initialized(cls):
        return cls._inited

    @classmethod
    def reset_state(cls):
        cls._instance = None
        cls._inited = False


class lazyproperty(object):

    """
    Define a read-only attribute as a property that only once computes 
    value on the first access. Value will be cached and not recomputed 
    on each access.
    """

    def __init__(self, func):
        self._func = func

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        value = self._func(instance)
        setattr(instance, self._func.__name__, value)
        return value


class ReadOnly(object):

    def __setattr__(self, name, value):
        if name not in self.__dict__:
            self.__dict__[name] = value
        else:
            raise ValueError(u'cannot change a const attribute')

    def __delattr__(self, name):
        raise ValueError(u'cannot delete a const attribute')
