"""Common base client."""

from socket import socket, SocketKind   # pylint: disable=E0611
from typing import Tuple


__all__ = ['Client']


class Client:
    """A basic client, common to Query and RCON."""

    def __init__(self, typ: SocketKind, host: str, port: int, *,
                 timeout: float = None):
        """Sets host an port."""
        self._socket = socket(type=typ)
        self.host = host
        self.port = port
        self.timeout = timeout

    def __enter__(self):
        """Conntects the socket."""
        self._socket.__enter__()
        self.connect()
        return self

    def __exit__(self, typ, value, traceback):
        """Delegates to the underlying socket's exit method."""
        self.close()
        return self._socket.__exit__(typ, value, traceback)

    @property
    def socket(self) -> Tuple[str, int]:
        """Returns a tuple of host and port."""
        return (self.host, self.port)

    def connect(self):
        """Conntects to the RCON server."""
        self._socket.settimeout(self.timeout)
        return self._socket.connect(self.socket)

    def close(self):
        """Disconnects from the RCON server."""
        return self._socket.close()