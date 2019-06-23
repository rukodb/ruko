from typing import Union, List, Mapping, Sequence

from ruko.binary_socket import BinarySocket
from ruko.command import Command
from ruko.empty_type import Empty
from ruko.empty_type import EmptyType
from ruko.serialize import with_len, json_to_bytes, bytes_to_json, DType
from ruko.utils import recursive_merge

Index = Union[str, list, tuple, int, None]
Json = Union[dict, list, int, float, bool, None]


class RukoClient:
    """Raw client to execute commands to server"""

    def __init__(self, ip: str, port: int):
        self.socket = BinarySocket(ip, port)

    def close(self):
        self.socket.close()

    @staticmethod
    def parse_key(key: Index) -> list:
        if key is ...:
            key = '---'
        if isinstance(key, str):
            return [key]
        if isinstance(key, int):
            return [str(key)]
        if key is None or key is ():
            return []
        return list(map(str, key))

    def get(self, key: Index = None, fields: List[str] = None, exclude: List[str] = None) -> Union[Json, EmptyType]:
        # TODO: Support dotted filters in fields and exclude
        key = self.parse_key(key)
        fields = fields or []
        exclude = exclude or []
        d = self._send(
            bytes([Command.GET]) +
            self._encode_key(key) +
            with_len(b''.join(with_len(i.encode()) for i in fields), len(fields)) +
            with_len(b''.join(with_len(i.encode()) for i in exclude), len(exclude))
        )
        return d

    def set(self, key: Index, value: Json, fallback=None):
        key = self.parse_key(key)
        return self._send(
            bytes([Command.SET]) +
            self._encode_key(key) +
            json_to_bytes(value, fallback)
        )

    def delete(self, key: Index):
        return self._send(
            bytes([Command.DELETE]) +
            self._encode_key(key)
        )

    def declare(self, key: Index, dtype: DType, indices: List[str] = None):
        key = self.parse_key(key)
        data = (
                bytes([Command.DECLARE]) +
                self._encode_key(key) +
                bytes([dtype])
        )
        data += with_len(b''.join(with_len(i.encode()) for i in indices or []), length=len(indices))
        return self._send(data)

    def lput(self, key: Index, value: Json, fallback=None):  # TODO: Detect error (append on dict)
        key = self.parse_key(key)
        return self._send(
            bytes([Command.LPUT]) +
            self._encode_key(key) +
            json_to_bytes(value, fallback)
        )

    def create_mapping(self, key: Index, pattern: Index):
        key = self.parse_key(key)
        pattern = self.parse_key(pattern)
        return self._send(
            bytes([Command.CREATE_MAPPING]) +
            self._encode_key(key) +
            self._encode_key(pattern)
        )

    def delete_mapping(self, key: Index):
        key = self.parse_key(key)
        return self._send(
            bytes([Command.DELETE_MAPPING]) +
            self._encode_key(key)
        )

    def get_mappings(self):
        return [(name, pattern.split('\x19')) for name, pattern in self._send(bytes([Command.GET_MAPPINGS]))]

    def linsert(self, key: Index, index: int, value: Json):
        # TODO: Add linsert command
        data = self.get(key)
        data.insert(index, value)
        self.set(key, data)

    def dupdate(self, key: Index, element=None, **params):
        # TODO: Add dupdate command
        # TODO: Detect error (update on list)
        key = self.parse_key(key)
        val = self.get(key)
        val.update(element, **params)
        self.set(key, val)

    def dmerge(self, key: Index, element=None, **params):
        # TODO: Add dmerge command
        # TODO: Detect error (merge on list)
        key = self.parse_key(key)
        new_dict = dict(element, **params)
        val = self.get(key)
        val = dict(recursive_merge(val, new_dict))
        self.set(key, val)

    def dgetkeys(self, key: Index):
        # TODO: Add dgetkeys command
        key = self.parse_key(key)
        val = self.get(key)
        if isinstance(val, Mapping):
            return list(val.keys())
        elif isinstance(val, Sequence):
            return list(range(len(val)))
        return Empty

    def contains(self, key: Index, item: str) -> bool:
        # TODO: Add dcontains command
        return item in self.dgetkeys(key)

    def dgetvalues(self, key: Index):
        # TODO: Add dgetkeys command
        key = self.parse_key(key)
        return list(self.get(key).values())

    def clear(self, key: Index):
        # TODO: Add clear command
        self.set(key, type(self.get(key))())

    def _encode_key(self, key):
        return with_len(b''.join(with_len(i.encode()) for i in key), length=len(key))

    def _send(self, data: bytes) -> Union[Json, EmptyType]:
        ret = self.socket.send(data)

        if not ret:
            return Empty
        return bytes_to_json(ret)[0]
