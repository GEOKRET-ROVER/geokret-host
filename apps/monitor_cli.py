### THE CODE IN THIS FILE WAS FULLY GENERATED WITH GEMINI 4 NEON

import time

from comms import Esp32Client
from comms import UdpTransport


def main() -> None:
    transport = UdpTransport()
    client = Esp32Client(transport)
    client.start()
    print("Nasłuchiwanie pakietów z ESP32... (Ctrl+C aby zakończyć)")

    try:
        while True:
            batches = client.get_pending_packets()

            for batch in batches:
                print(f"\nseq={batch.seq} | punktów: {len(batch.points)} | łącznie pakietów: {client.stats.received_packets}")
                for p in batch.points:
                    print(f"  t={p.t_ms:8d} ms | angle={p.angle:3d}° | dist={p.dist_cm:4d} cm | sig={p.signal:5d}")

            time.sleep(0.02)  # ~50 Hz, żeby pętla nie paliła 100% CPU
    except KeyboardInterrupt:
        print("\nZamykanie...")
    finally:
        client.stop()


if __name__ == "__main__":
    main()