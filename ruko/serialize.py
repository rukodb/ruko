import struct
from enum import IntEnum
from typing import Any, Callable


class DType(IntEnum):
    EMPTY = 0
    NULL = 1
    BOOL = 2
    INT = 3
    FLOAT = 4
    STRING = 5
    LIST = 6
    DICT = 7


def bytes_to_u32(x):
    return struct.unpack('<L', x)[0]


def u32_to_bytes(x) -> bytes:
    return bytes(struct.pack('<L', x))


def bytes_to_f32(x):
    return struct.unpack('<f', x)[0]


def f32_to_bytes(x) -> bytes:
    return bytes(struct.pack('<f', x))


def bytes_to_i32(x):
    return struct.unpack('<i', x)[0]


def i32_to_bytes(x):
    return struct.pack('<i', x)


def with_len(bs: bytes, length=None) -> bytes:
    if length is None:
        length = len(bs)
    return u32_to_bytes(length) + bs


def bytes_to_null(_x, p=0) -> (None, int):
    return None, p


def bytes_to_bool(x, p=0) -> (bool, int):
    return x[0] != 0, p + 1


def bytes_to_int(x, p=0) -> (int, int):
    n = bytes_to_i32(x[p:p + 4])
    return n, p + 4


def bytes_to_float(x, p=0) -> (int, int):
    n = bytes_to_f32(x[p:p + 4])
    return n, p + 4


def bytes_to_str(x, p=0) -> (str, int):
    sz = bytes_to_u32(x[p:p + 4])
    p += 4
    data = x[p:p + sz].decode()
    p += sz
    return data, p


def bytes_to_list(x, p=0) -> (list, int):
    ls = []
    sz = bytes_to_u32(x[p:p + 4])
    p += 4
    for _ in range(sz):
        obj, p = bytes_to_json(x, p)
        ls.append(obj)
    return ls, p


def bytes_to_dict(x: bytes, p=0) -> (dict, int):
    d = {}
    sz = bytes_to_u32(x[p:p + 4])
    p += 4
    for _ in range(sz):
        key, p = bytes_to_str(x, p)
        d[key], p = bytes_to_json(x, p)

    return d, p


def bytes_to_json(x: bytes, p=0) -> (Any, int):
    func = {
        DType.NULL: bytes_to_null,
        DType.BOOL: bytes_to_bool,
        DType.INT: bytes_to_int,
        DType.FLOAT: bytes_to_float,
        DType.STRING: bytes_to_str,
        DType.LIST: bytes_to_list,
        DType.DICT: bytes_to_dict
    }[DType(x[p])]
    a, b = func(x, p + 1)
    return a, b


def raise_key_error(x, _key):
    raise ValueError('Cannot serialize: {}'.format(x))


def json_to_bytes(a: Any, fallback=None, key=()) -> bytes:
    func = {
        type(None): lambda x: bytes([DType.NULL]),
        bool: lambda x: bytes([DType.BOOL, int(x)]),
        int: lambda x: bytes([DType.INT]) + u32_to_bytes(x),
        float: lambda x: bytes([DType.FLOAT]) + f32_to_bytes(x),
        str: lambda x: bytes([DType.STRING]) + with_len(x.encode()),
        list: lambda x: bytes([DType.LIST]) + with_len(b''.join(
            json_to_bytes(v, fallback, key + (i,)) for i, v in enumerate(x)
        ), len(x)),
        dict: lambda x: bytes([DType.DICT]) + with_len(b''.join(
            with_len(k.encode()) + json_to_bytes(v, fallback, key + (k,)) for k, v in x.items()
        ), len(x))
    }.get(type(a))  # type: Callable
    if not func:
        return (fallback or raise_key_error)(a, key)
    return func(a)
