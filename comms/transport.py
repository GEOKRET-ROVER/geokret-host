import socket

from typing import Protocol

UDP_PORT = 8080

class Transport(Protocol):

    def open(self) -> None:
        ...

    def close(self) -> None:
        ...

    def recv(self, timeout: float) -> bytes | None:
        ...

    def send(self, data: bytes) -> None:
        ...


class UdpTransport:
    def __init__(
        self,
        remote_addr: tuple[str, int] | None = None,
        buffer_size: int = 2048,
    ) -> None:
        self._remote_addr = remote_addr
        self._buffer_size = buffer_size
        self._sock: socket.socket | None = None

    def open(self) -> None:
        if self._sock is not None:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", UDP_PORT))
        self._sock = sock

    def close(self) -> None:
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def recv(self, timeout: float) -> bytes | None:
        if self._sock is None:
            raise RuntimeError("UdpTransport is not open yet.")

        self._sock.settimeout(timeout)
        try:
            data, addr = self._sock.recvfrom(self._buffer_size)
        except (socket.timeout, TimeoutError, BlockingIOError):
            return None

        # remember the sender if it was not explicitly given in the constructor
        if self._remote_addr is None:
            self._remote_addr = addr

        return data

    def send(self, data: bytes) -> None:
        raise RuntimeError("NotImplementedYet")
    
        if self._sock is None:
            raise RuntimeError("Transport UDP nie jest otwarty. Wywołaj najpierw open().")
        if self._remote_addr is None:
            raise RuntimeError("Nieznany adres docelowy ESP32 (nie odebrano jeszcze żadnego pakietu).")

        self._sock.sendto(data, self._remote_addr)