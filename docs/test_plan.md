# Hardware Validation Test Plan

## Objective

Verify that the Arduino sensor testbench can capture analog sensor behavior, stream usable CSV data, and support repeatable analysis of range, noise, and outliers.

## Equipment

- Arduino Uno or compatible board
- USB cable
- Potentiometer or analog voltage sensor
- Breadboard and jumper wires
- Digital multimeter
- Optional oscilloscope or Analog Discovery 2
- Computer with Python 3.10+

## Wiring

| Signal | Arduino Pin |
| --- | --- |
| Sensor output | A0 |
| Sensor ground | GND |
| Sensor power | 5V or 3.3V, depending on sensor rating |

For a potentiometer demo, connect the outer pins to `5V` and `GND`, then connect the wiper to `A0`.

## Firmware Setup

1. Open `firmware/sensor_testbench/sensor_testbench.ino` in the Arduino IDE.
2. Select the correct board and serial port.
3. Upload the sketch.
4. Confirm the serial monitor prints:

```text
sample_id,timestamp_ms,raw_adc,voltage_mv,filtered_mv,digital_state
```

## Test Cases

| ID | Test | Procedure | Expected Result |
| --- | --- | --- | --- |
| T01 | Serial format | Open serial monitor at 115200 baud | CSV header and numeric rows appear |
| T02 | Low input | Turn potentiometer near GND | Voltage approaches 0 mV |
| T03 | High input | Turn potentiometer near 5V | Voltage approaches 5000 mV |
| T04 | Sweep response | Slowly sweep from low to high | Raw and filtered values increase smoothly |
| T05 | Stability | Hold the input still for 30 seconds | Analyzer reports low outlier ratio |
| T06 | Noise spike | Tap or disturb the input wire briefly | Analyzer detects one or more outliers |

## Data Capture

```bash
python -m testbench log --port COM3 --seconds 30 --output data/hardware_run.csv
python -m testbench analyze data/hardware_run.csv
```

## Pass Criteria

- At least 50 samples are captured.
- Data contains all required CSV fields.
- Voltage remains between 0 mV and 5000 mV.
- Outlier ratio is below 3 percent during a stable-input run.
- Results are reproducible across at least three captures.

## Notes For Improvement

- Compare Arduino voltage readings against a digital multimeter.
- Add a two-point calibration routine.
- Record oscilloscope screenshots for noisy-input cases.
- Add a summary report generated from each run.
