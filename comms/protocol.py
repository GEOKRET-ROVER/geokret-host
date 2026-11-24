from dataclasses import dataclass
from enum import IntEnum
import struct

class PacketType(IntEnum):
    SCAN = 1
    DRIVE_CMD = 2


@dataclass(slots=True, frozen=True)
class ScanPoint:
    angle: int     # <H (2 B)
    dist_cm: int   # <H (2 B)
    signal: int     # <h (2 B)
    t_ms: int      # <I (4 B)


@dataclass(slots=True, frozen=True)
class ScanBatch:
    seq: int
    points: tuple[ScanPoint, ...]


@dataclass(slots=True, frozen=True)
class DriveCommand:
    # TODO someday will reach here
    pass



PROTOCOL_VERSION = 1

HEADER_FMT = "<BBH"   # version, type, seq - 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)

POINT_FMT = "<HHhI"   # angle, distCm, signal, tMs - 10 bytes
POINT_SIZE = struct.calcsize(POINT_FMT)
assert(HEADER_SIZE == 4)
assert(POINT_SIZE == 10)


def decode_packet(data: bytes) -> ScanBatch | None:
    if len(data) < HEADER_SIZE:
        print("data shorter than the header itself - ignoring")
        return None
    version, ptype, seq = struct.unpack_from(HEADER_FMT, data, 0)
    if version != PROTOCOL_VERSION:
        print(f"Not compatible packet version: {version} - ignoring")
        return None
    if ptype != PacketType.SCAN:
        print(f"invalid type scan: {ptype}. Expected ScanPoint - ignoring")
        return None
    payload = memoryview(data)[HEADER_SIZE:]
    if len(payload) % POINT_SIZE != 0:
        print(f"the packet does not contain a multiple of bytes for a single ScanPoint, but: {len(payload)} - ignoring")
        return None

    points = tuple(
        ScanPoint(angle, dist_cm, signal, t_ms)
        for angle, dist_cm, signal, t_ms in struct.iter_unpack(POINT_FMT, payload)
    )
    return ScanBatch(seq=seq, points=points)