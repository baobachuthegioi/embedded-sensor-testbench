from __future__ import annotations

import csv
import math
import random
from pathlib import Path


FIELDNAMES = [
    "sample_id",
    "timestamp_ms",
    "raw_adc",
    "voltage_mv",
    "filtered_mv",
    "digital_state",
]


def generate_samples(
    *,
    samples: int = 250,
    interval_ms: int = 20,
    base_mv: float = 1650.0,
    amplitude_mv: float = 520.0,
    noise_mv: float = 18.0,
    seed: int = 42,
) -> list[dict[str, int | float]]:
    if samples <= 0:
        raise ValueError("samples must be positive")
    if interval_ms <= 0:
        raise ValueError("interval_ms must be positive")

    rng = random.Random(seed)
    rows: list[dict[str, int | float]] = []
    filtered_mv = base_mv

    for sample_id in range(samples):
        phase = (sample_id / max(samples - 1, 1)) * math.tau * 2
        voltage_mv = base_mv + (amplitude_mv * math.sin(phase)) + rng.gauss(0.0, noise_mv)
        voltage_mv = min(5000.0, max(0.0, voltage_mv))
        raw_adc = round((voltage_mv / 5000.0) * 1023)
        quantized_mv = (raw_adc * 5000.0) / 1023.0
        filtered_mv = (0.18 * quantized_mv) + (0.82 * filtered_mv)
        digital_state = int(filtered_mv >= 2500.0)

        rows.append(
            {
                "sample_id": sample_id,
                "timestamp_ms": sample_id * interval_ms,
                "raw_adc": raw_adc,
                "voltage_mv": round(quantized_mv, 2),
                "filtered_mv": round(filtered_mv, 2),
                "digital_state": digital_state,
            }
        )

    return rows


def write_csv(rows: list[dict[str, int | float]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
