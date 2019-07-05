from collections import MutableMapping

from typing import Iterator, MutableSequence, Union

from ruko.context import RContext
from ruko.empty_type import Empty
from ruko.ruko_client import RukoClient, Index, Json


class RDict(MutableMapping, MutableSequence):
    """High level Python interface to Ruko database"""

    @classmethod
    def client(cls, ip: str = "127.0.0.1", port: int = 44544, key_error=KeyError):
        """Create a new connection"""
        return cls([], RContext(ip, port), key_error)

    def __init__(self, db_key, context: RContext, key_error=KeyError):
        """Typically, you want to use RDict.client() instead"""
        self.key = RukoClient.parse_key(db_key)
        self.context = context
        self.key_error = key_error

    @property
    def rk(self):
        return self.context.get()

    def __iter__(self) -> Iterator[str]:
        keys = self.rk.dgetkeys(self.key)
        if keys is Empty:
            return iter(self.get())
        return iter(keys)

    def items(self) -> Iterator[tuple]:
        return self().items()

    def insert(self, index: int, obj: Json) -> None:
        self.rk.linsert(self.key, index, obj)

    def keys(self):
        return self.rk.dgetkeys(self.key)

    def values(self):
        return self.rk.dgetvalues(self.key)

    def by(self, key: str) -> 'RDict':
        return self.child(self.sub_key([key + ':']))

    def get(self, item=None, default=None, fields=None, exclude=None):
        item = RukoClient.parse_key(item)
        val = self.rk.get(self.sub_key(item), fields, exclude)
        if val is Empty:
            return default
        return val

    def update(self, element=None, **params):
        return self.rk.dupdate(self.key, element, **params)

    def merge(self, element=None, **params):
        return self.rk.dmerge(self.key, element, **params)

    def clear(self):
        self.rk.clear(self.key)

    def append(self, value):
        self.rk.lput(self.key, value)

    @staticmethod
    def concat(a: list, b: list):
        if a and a[-1].endswith(':') and b:
            a = list(a)
            a[-1] = a[-1] + (b[0] or '~')
            return a + b[1:]
        return a + b

    def sub_key(self, b: list):
        return self.concat(self.key, b)

    def child(self, full_key) -> 'RDict':
        return RDict(full_key, self.context, self.key_error)

    def setdefault(self, key, default=None) -> 'RDict':
        key = RukoClient.parse_key(key)
        new_key = self.concat(self.key, key)
        cur_val = self.rk.get(new_key)
        if cur_val is Empty:
            self.rk.set(new_key, default)
        return self.child(new_key)

    def create_mapping(self, key, filters) -> 'RDict':
        key = RukoClient.parse_key(key)
        new_key = self.sub_key(key)
        if isinstance(filters, list):
            if filters and isinstance(filters[0], (str, int)):
                if any(isinstance(i, str) and '.' in i for i in filters):
                    filters = [i.split('.') for i in filters]
                else:
                    filters = [filters]
            else:
                pass  # Already in right format
        else:
            if isinstance(filters, str) and '.' in filters:
                filters = [filters.split('.')]
            else:
                filters = [RukoClient.parse_key(filters)]
        for filt in filters:
            self.rk.create_mapping(new_key, filt)
        return self.child(new_key)

    def delete_mapping(self, key):
        key = RukoClient.parse_key(key)
        self.rk.delete_mapping(self.sub_key(key))

    def get_mappings(self):
        return self.rk.get_mappings()

    def __contains__(self, item):
        return self.rk.contains(self.key, item)

    def __getitem__(self, item: Index) -> Union['RDict', str, int, list, dict, bool, None]:
        item = RukoClient.parse_key(item)
        return self.child(self.sub_key(item))

    def __call__(self, fields=None, exclude=None):
        val = self.rk.get(self.key, fields, exclude)
        if val is Empty:
            raise self.key_error(self.key[-1])
        return val

    def __delitem__(self, key):
        key = RukoClient.parse_key(key)
        return self.rk.delete(self.sub_key(key))

    def __setitem__(self, key, value):
        key = RukoClient.parse_key(key)
        self.rk.set(self.sub_key(key), value)

    def __len__(self):  # TODO: Add len command
        return len(self.get())

    def __repr__(self):
        return '<RDict key={}>'.format('.'.join(map(str, self.key)))

    def __eq__(self, other):
        if isinstance(other, RDict):
            other_val = other.get()
        else:
            other_val = other
        my_val = self.get()
        return my_val == other_val
