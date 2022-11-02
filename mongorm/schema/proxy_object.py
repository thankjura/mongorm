__all__ = ['ProxyObject']

from typing import Callable

MUTABLE_METHODS = {'extend', 'append', 'clear', 'remove', 'pop', 'insert',
                   'reverse', 'sort', 'popitem', 'update', '__delitem__', '__setitem__'}


OVERRIDE_MAGIC_METHODS = [
    '__add__', '__contains__', '__delitem__', '__eq__', '__format__',
    '__ge__', '__getitem__', '__gt__', '__hash__', '__iadd__', '__imul__',
    '__ior__', '__iter__', '__le__', '__len__', '__lt__', '__mul__', '__ne__',
    '__or__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__',
    '__rmul__', '__ror__', '__setitem__', '__sizeof__', '__class__'
]

DICT_METHODS = dir({})


class ProxyObject(object):
    __slots__ = ['_obj', '__weakref__']

    def __init__(self, obj, on_change: Callable = None):
        object.__setattr__(self, '_obj', obj)
        object.__setattr__(self, '_on_change', on_change)

    def __on_change(self):
        if object.__getattribute__(self, '_on_change'):
            object.__getattribute__(self, '_on_change')()

    def __wrap_out(self, out):
        if isinstance(out, (set, list, dict)):
            return ProxyObject(out, object.__getattribute__(self, '_on_change'))
        return out

    def __getattribute__(self, name):
        obj = object.__getattribute__(self, '_obj')
        if isinstance(obj, dict) and name not in DICT_METHODS:
            out = obj.get(name)
        else:
            out = getattr(obj, name)
        if name in MUTABLE_METHODS:
            object.__getattribute__(self, '_ProxyObject__on_change')()

        return out
        # return object.__getattribute__(self, '_ProxyObject__wrap_out')(out)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, '_obj'), name)
        object.__getattribute__(self, '_ProxyObject__on_change')()

    def __setattr__(self, name, value):
        obj = object.__getattribute__(self, '_obj')
        if isinstance(obj, dict) and name not in DICT_METHODS:
            obj[name] = value
        else:
            setattr(obj, name, value)
        object.__getattribute__(self, '_ProxyObject__on_change')()

    def __nonzero__(self):
        return bool(object.__getattribute__(self, '_obj'))

    def __str__(self):
        return str(object.__getattribute__(self, '_obj'))

    def __repr__(self):
        return repr(object.__getattribute__(self, '_obj'))

    @property
    def __class__(self):
        return getattr(object.__getattribute__(self, '_obj'), '__class__')

    @classmethod
    def _create_class_proxy(cls, target_class):
        def make_method(method_name):
            def method(self, *args, **kw):
                out = getattr(object.__getattribute__(self, '_obj'), method_name)(*args, **kw)
                if method_name in MUTABLE_METHODS:
                    object.__getattribute__(self, '_ProxyObject__on_change')()
                return out

            return method

        namespace = {}
        for name in OVERRIDE_MAGIC_METHODS:
            if hasattr(target_class, name):
                namespace[name] = make_method(name)
        return type('%s(%s)' % (cls.__name__, target_class.__name__), (cls,), namespace)

    def __new__(cls, obj, *args, **kwargs):
        try:
            cache = cls.__dict__['_class_proxy_cache']
        except KeyError:
            cls._class_proxy_cache = cache = {}
        try:
            target_class = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = target_class = cls._create_class_proxy(obj.__class__)
        ins = object.__new__(target_class)
        target_class.__init__(ins, obj, *args, **kwargs)
        return ins
