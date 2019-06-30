import socket
from contextlib import suppress
from threading import Lock

from ruko.serialize import bytes_to_u32, u32_to_bytes


class BinarySocket:
    """A client for simple length-prefixed socket communication"""

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = self.open_socket()
        self.lock = Lock()

    def open_socket(self):
        s = socket.socket()
        s.connect((self.ip, self.port))
        return s

    def send(self, msg: bytes) -> bytes:
        try:
            return self._send(msg)
        except (ConnectionAbortedError, OSError):
            print('Reconnecting...')
            self.socket = self.open_socket()
            return self._send(msg)

    def _send(self, msg: bytes):
        len_bytes = u32_to_bytes(len(msg))
        bs = len_bytes + msg

        with self.lock:
            self.socket.sendall(bs)
            length = bytes_to_u32(self._read_bytes(4))
            return self._read_bytes(length)

    def close(self):
        with self.lock:
            self._close()

    def _close(self):
        with suppress(OSError):
            self.socket.shutdown(2)
        self.socket.close()

    def _read_bytes(self, n: int) -> bytes:
        buf = b''
        while len(buf) < n:
            new_data = self.socket.recv(n - len(buf))
            if not new_data:
                self._close()
                raise ConnectionAbortedError
            buf += new_data
        return buf
