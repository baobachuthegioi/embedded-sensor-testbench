# Embedded Sensor Testbench

Arduino firmware plus a Python validation toolkit for testing analog sensor behavior over serial.

This project is designed for Computer Engineering internship applications. It shows embedded C/C++, hardware/software validation, serial communication, data analysis, test planning, and automated checks in one small repo.

## What It Does

- Streams Arduino sensor readings as CSV over USB serial.
- Converts raw ADC values to millivolts.
- Applies a lightweight exponential moving average on the microcontroller.
- Logs real hardware runs from a serial port.
- Generates simulated runs when hardware is not connected.
- Analyzes captured data for range, noise, outliers, and pass/fail status.
- Includes a written hardware validation test plan.

## Project Architecture

```text
firmware/sensor_testbench/   Arduino C++ firmware
src/testbench/               Python capture, simulation, and analysis tools
tests/                       Unit tests for analysis behavior
docs/                        Test plan and interview notes
data/                        Example captured or simulated runs
```

## Quick Demo

Run the demo without hardware:

```bash
python -m pip install -e .
python -m testbench simulate --samples 250 --output data/demo_run.csv
python -m testbench analyze data/demo_run.csv
python -m unittest discover -s tests
```

If you do not install the package, run commands from the repo root and set `PYTHONPATH` first:

```powershell
$env:PYTHONPATH = "src"
python -m testbench simulate --samples 250 --output data/demo_run.csv
python -m testbench analyze data/demo_run.csv
```

On macOS/Linux, use `export PYTHONPATH=src`.

## Hardware Mode

1. Upload `firmware/sensor_testbench/sensor_testbench.ino` to an Arduino Uno or compatible board.
2. Connect a potentiometer or analog sensor output to `A0`.
3. Connect sensor ground to Arduino `GND`.
4. Open a serial connection at `115200` baud.
5. Log a run:

```bash
python -m pip install -e ".[serial]"
python -m testbench log --port COM3 --seconds 30 --output data/hardware_run.csv
python -m testbench analyze data/hardware_run.csv
```

On macOS/Linux, the port will usually look like `/dev/tty.usbmodem...` or `/dev/ttyACM0`.

## Example Output

```text
Samples: 250
Duration: 4980 ms
Voltage avg/min/max: 1651.9 / 1104.6 / 2189.6 mV
Peak-to-peak noise: 1085.0 mV
Outlier ratio: 0.00%
Verdict: PASS
```

## Validation Criteria

The analyzer flags a run if:

- sample count is too small
- voltage is outside the expected ADC range
- outlier ratio is above the configured limit
- peak-to-peak noise is above the configured limit

The defaults are intentionally conservative and easy to tune in `src/testbench/analysis.py`.

## Why This Helps With Internships

This repo is built to support embedded systems, hardware test, validation, and computer engineering internship roles. It gives you a concrete story:

> I built an Arduino-based sensor validation testbench with C++ firmware and a Python analysis CLI. The system captures ADC readings over serial, filters measurements, detects outliers, generates repeatable simulated data, and documents a hardware test plan with automated unit tests.

Resume bullet:

> Built an Arduino sensor validation testbench using C++ and Python to stream ADC measurements over serial, analyze voltage stability/noise/outliers, and document repeatable hardware test procedures with automated unit tests.

## Roadmap

- Add live matplotlib plots for hardware runs.
- Add calibration mode using two known voltage points.
- Save summary reports as Markdown or PDF.
- Add support for multiple analog channels.
- Add GitHub release screenshots and a short demo video.
# embedded-sensor-testbench
Arduino C++ firmware and Python validation tools for sensor test automation.
