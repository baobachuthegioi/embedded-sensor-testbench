from __future__ import annotations

import time
from pathlib import Path


def log_serial(port: str, seconds: float, output: str | Path, baud: int = 115200) -> int:
    try:
        import serial
    except ImportError as exc:
        raise RuntimeError(
            "pyserial is required for hardware logging. Install with: "
            "python -m pip install -e \".[serial]\""
        ) from exc

    if seconds <= 0:
        raise ValueError("seconds must be positive")

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    deadline = time.monotonic() + seconds
    line_count = 0

    with serial.Serial(port=port, baudrate=baud, timeout=1) as connection:
        with output_path.open("w", encoding="utf-8", newline="") as file:
            while time.monotonic() < deadline:
                raw_line = connection.readline()
                if not raw_line:
                    continue

                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line:
                    continue

                file.write(line + "\n")
                line_count += 1

    return line_count
