### THE CODE IN THIS FILE WAS FULLY GENERATED WITH GEMINI 4 NEON

import math
import sys
import time

from comms import Esp32Client, UdpTransport

# --- Konfiguracja radaru ---
MAX_DIST_CM = 100   # zasięg radaru (wszystko dalej nie zmieści się na okręgu)
RADIUS = 25         # promień w wierszach terminala (wysokość = 2*RADIUS + 1)
ASPECT = 2.0        # korekta proporcji znaków w terminalu (znak jest ~2x wyższy niż szerszy)
FPS = 15            # częstotliwość odświeżania ekranu


def render_radar(scans: dict[int, int], last_angle: int | None, rx_count: int) -> str:
    width = int(RADIUS * 2 * ASPECT) + 1
    height = RADIUS * 2 + 1
    cx = width // 2
    cy = height // 2

    # 1. Pusta siatka
    grid = [[" " for _ in range(width)] for _ in range(height)]

    # 2. Okrąg zasięgu (z kropek)
    for deg in range(0, 360, 4):
        rad = math.radians(deg)
        gx = int(round(cx + RADIUS * ASPECT * math.sin(rad)))
        gy = int(round(cy - RADIUS * math.cos(rad)))
        if 0 <= gx < width and 0 <= gy < height:
            grid[gy][gx] = "."

    # 3. Promień wskazujący, gdzie obecnie patrzy LIDAR (z najnowszej paczki)
    if last_angle is not None:
        rad = math.radians(last_angle)
        steps = int(RADIUS * ASPECT)
        for step in range(1, steps + 1):
            r = (step / steps) * RADIUS
            gx = int(round(cx + r * ASPECT * math.sin(rad)))
            gy = int(round(cy - r * math.cos(rad)))
            if 0 <= gx < width and 0 <= gy < height:
                grid[gy][gx] = ":" if step < steps else "O"

    # 4. Naniesienie zmierzonych punktów (0° = góra/przód, 90° = prawo)
    for angle, dist_cm in scans.items():
        if dist_cm <= 0 or dist_cm > MAX_DIST_CM:
            continue
        r = (dist_cm / MAX_DIST_CM) * RADIUS
        rad = math.radians(angle)
        gx = int(round(cx + r * ASPECT * math.sin(rad)))
        gy = int(round(cy - r * math.cos(rad)))
        if 0 <= gx < width and 0 <= gy < height:
            grid[gy][gx] = "#"

    # Środek (łazik / wieżyczka)
    grid[cy][cx] = "@"

    # 5. Złożenie ramki w jeden string
    header = (
        f"GEOKRET RADAR | zasięg: {MAX_DIST_CM} cm | "
        f"pakiety: {rx_count} | kąt: {last_angle if last_angle is not None else '---'}°   "
    )
    lines = [header, "-" * width]
    lines.extend("".join(row) for row in grid)
    return "\n".join(lines)


def main() -> None:
    transport = UdpTransport()
    client = Esp32Client(transport)
    client.start()

    # Mapa: kąt (0..359) -> ostatnia zmierzona odległość w cm
    scans: dict[int, int] = {}
    last_angle: int | None = None

    # Wyczyść ekran i ukryj kursor
    sys.stdout.write("\033[2J\033[?25l")
    sys.stdout.flush()

    try:
        while True:
            for batch in client.get_pending_packets():
                for p in batch.points:
                    scans[p.angle % 360] = p.dist_cm
                    last_angle = p.angle

            frame = render_radar(scans, last_angle, client.stats.received_packets)
            # \033[H przenosi kursor na początek ekranu bez jego czyszczenia
            sys.stdout.write("\033[H" + frame)
            sys.stdout.flush()

            time.sleep(1.0 / FPS)
    except KeyboardInterrupt:
        pass
    finally:
        # Przywróć kursor po wyjściu
        sys.stdout.write("\033[?25h\nZamykanie...\n")
        sys.stdout.flush()
        client.stop()


if __name__ == "__main__":
    main()