from __future__ import annotations

import csv
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_FIELDS = (
    "sample_id",
    "timestamp_ms",
    "raw_adc",
    "voltage_mv",
    "filtered_mv",
    "digital_state",
)


@dataclass(frozen=True)
class Sample:
    sample_id: int
    timestamp_ms: int
    raw_adc: int
    voltage_mv: float
    filtered_mv: float
    digital_state: int


def read_samples(path: str | Path) -> list[Sample]:
    """Read CSV samples emitted by the Arduino firmware or simulator."""
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = [field for field in REQUIRED_FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required CSV fields: {', '.join(missing)}")

        return [_row_to_sample(row) for row in reader if any(row.values())]


def _row_to_sample(row: dict[str, str]) -> Sample:
    return Sample(
        sample_id=int(row["sample_id"]),
        timestamp_ms=int(row["timestamp_ms"]),
        raw_adc=int(row["raw_adc"]),
        voltage_mv=float(row["voltage_mv"]),
        filtered_mv=float(row["filtered_mv"]),
        digital_state=int(row["digital_state"]),
    )


def moving_average(values: Iterable[float], window: int = 5) -> list[float]:
    if window <= 0:
        raise ValueError("window must be positive")

    values_list = list(values)
    averaged: list[float] = []
    for index in range(len(values_list)):
        start = max(0, index - window + 1)
        chunk = values_list[start : index + 1]
        averaged.append(sum(chunk) / len(chunk))
    return averaged


def summarize(samples: list[Sample]) -> dict[str, float | int]:
    if not samples:
        raise ValueError("At least one sample is required")

    voltages = [sample.voltage_mv for sample in samples]
    filtered = [sample.filtered_mv for sample in samples]
    duration_ms = samples[-1].timestamp_ms - samples[0].timestamp_ms
    avg_interval_ms = duration_ms / (len(samples) - 1) if len(samples) > 1 else 0.0

    return {
        "sample_count": len(samples),
        "duration_ms": duration_ms,
        "avg_interval_ms": avg_interval_ms,
        "voltage_min_mv": min(voltages),
        "voltage_max_mv": max(voltages),
        "voltage_avg_mv": statistics.fmean(voltages),
        "filtered_avg_mv": statistics.fmean(filtered),
        "noise_pp_mv": max(voltages) - min(voltages),
        "noise_rms_mv": _rms_noise(voltages),
        "digital_high_count": sum(sample.digital_state for sample in samples),
    }


def detect_outliers(samples: list[Sample], threshold_mv: float = 250.0, window: int = 8) -> list[Sample]:
    if threshold_mv < 0:
        raise ValueError("threshold_mv cannot be negative")

    voltages = [sample.voltage_mv for sample in samples]
    baseline = moving_average(voltages, window=window)
    return [
        sample
        for sample, expected in zip(samples, baseline)
        if abs(sample.voltage_mv - expected) > threshold_mv
    ]


def validate_run(
    samples: list[Sample],
    *,
    expected_min_mv: float = 0.0,
    expected_max_mv: float = 5000.0,
    min_samples: int = 50,
    max_noise_pp_mv: float = 1500.0,
    max_outlier_ratio: float = 0.03,
) -> dict[str, object]:
    summary = summarize(samples)
    outliers = detect_outliers(samples)
    outlier_ratio = len(outliers) / len(samples)

    failures: list[str] = []
    if len(samples) < min_samples:
        failures.append(f"sample count below {min_samples}")
    if summary["voltage_min_mv"] < expected_min_mv:
        failures.append(f"voltage below {expected_min_mv:.1f} mV")
    if summary["voltage_max_mv"] > expected_max_mv:
        failures.append(f"voltage above {expected_max_mv:.1f} mV")
    if summary["noise_pp_mv"] > max_noise_pp_mv:
        failures.append(f"peak-to-peak noise above {max_noise_pp_mv:.1f} mV")
    if outlier_ratio > max_outlier_ratio:
        failures.append(f"outlier ratio above {max_outlier_ratio:.1%}")

    return {
        "passed": not failures,
        "failures": failures,
        "outlier_count": len(outliers),
        "outlier_ratio": outlier_ratio,
        "summary": summary,
    }


def _rms_noise(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0

    mean = statistics.fmean(values)
    return math.sqrt(statistics.fmean([(value - mean) ** 2 for value in values]))
