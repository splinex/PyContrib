'''
Enumerator class

Usage sample:

class Enum(metaclass=EnumMeta):
    __items__ = ['a', 'b', 'c']

print(Enum.c)
2
print(Enum.repr(1))
'b'
'''

class EnumMeta:
    def __init__(cls, name, bases, nmspc):
        cls.__map__ = dict()
        i = 0
        for item in nmspc.get('__items__', []):
            setattr(cls, item, i)
            cls.__map__[i] = item
            i += 1
        cls.repr = lambda i: cls.__map__[i] if i in cls.__map__ else i
        def lst():
            return list(cls.__map__.keys())
        cls.list = lst
