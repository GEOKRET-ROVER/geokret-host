from dataclasses import dataclass

from .transport import Transport
from . import protocol

@dataclass(slots=True)
class ClientStats:
    received_packets: int = 0
    lost_packets: int = 0
    duplicate_packets: int = 0
    out_of_order_packets: int = 0

class Esp32Client:
    def __init__(
        self,
        transport: Transport
    ) -> None:
        self._transport = transport
        self._last_seq: int | None = None
        self._last_rx_time: float = 0.0
        self.stats = ClientStats()

    def start(self) -> None:
        self._transport.open()

    def stop(self) -> None:
        self._transport.close()

    def get_pending_packets(self) -> list[protocol.ScanBatch]:
        batches = []

        while True:
            raw_batch = self._transport.recv(0.0)
            if raw_batch is None:
                break

            batch = protocol.decode_packet(raw_batch)
            if batch is None:
                continue

            self.stats.received_packets += 1
            batches.append(batch)
        return batches

    # def _accept_sequence(self, seq: int) -> bool:
    #     if self._last_seq is None:
    #         self._last_seq = seq
    #         return True
            