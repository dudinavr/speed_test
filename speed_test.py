import argparse
import time

import requests

CHUNK_SIZE = 64 * 1024

BYTES_IN_MB = 1024 * 1024

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def download(url: str, timeout: float = 30.0) -> tuple[float, int]:
    start = time.perf_counter()

    response = requests.get(url, stream=True, timeout=timeout, headers=HEADERS)
    response.raise_for_status()

    total_bytes = 0
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        total_bytes += len(chunk)

    elapsed = time.perf_counter() - start
    return elapsed, total_bytes


def measure_speed(url: str, num_requests: int = 10) -> None:
    times: list[float] = []
    sizes: list[int] = []

    for i in range(1, num_requests + 1):
        try:
            elapsed, size = download(url)
        except requests.RequestException as e:
            print(f"[{i}/{num_requests}] Ошибка запроса: {e}")
            continue

        times.append(elapsed)
        sizes.append(size)

        speed_mb_s = (size / BYTES_IN_MB) / elapsed if elapsed > 0 else 0.0
        print(
            f"[{i:2d}/{num_requests}] "
            f"время={elapsed:6.3f} с   "
            f"объём={size / BYTES_IN_MB:7.2f} МБ   "
            f"скорость={speed_mb_s:6.2f} МБ/с"
        )

    if not times:
        print("\nНи один запрос не выполнился успешно.")
        return

    total_bytes = sum(sizes)
    total_time = sum(times)
    avg_time = total_time / len(times)
    total_mb = total_bytes / BYTES_IN_MB

    avg_speed_mb_s = total_mb / total_time

    print("\n--- Итог ---")
    print(f"Успешных запросов:     {len(times)} из {num_requests}")
    print(f"Среднее время запроса: {avg_time:.3f} с")
    print(f"Скачано всего:         {total_mb:.2f} МБ")
    print(f"Средняя скорость:      {avg_speed_mb_s:.2f} МБ/с")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Замеряет скорость скачивания, обращаясь к заданному URL N раз подряд."
    )
    parser.add_argument(
        "url",
        help="URL файла для скачивания",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=10,
        help="Количество последовательных запросов (по умолчанию 10)",
    )
    args = parser.parse_args()

    measure_speed(args.url, args.num_requests)


if __name__ == "__main__":
    main()