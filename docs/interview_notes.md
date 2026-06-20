# Interview Notes

## Thirty-Second Pitch

I built an embedded sensor validation testbench that combines Arduino C++ firmware with a Python analysis CLI. The firmware streams ADC readings over serial, and the Python tool can log real hardware data, generate simulated data, detect outliers, and validate voltage/noise behavior. I also wrote a test plan and unit tests so the project looks like a small engineering workflow, not only a class demo.

## Skills Demonstrated

- Embedded C++ firmware
- Arduino ADC sampling
- Serial communication
- Hardware/software validation
- Python CLI development
- CSV data analysis
- Unit testing
- Technical documentation

## Resume Bullet

Built an Arduino sensor validation testbench using C++ and Python to stream ADC measurements over serial, analyze voltage stability/noise/outliers, and document repeatable hardware test procedures with automated unit tests.

## Interview Talking Points

- Why serial CSV is useful for quick hardware validation.
- How the firmware converts ADC counts to millivolts.
- Why filtering helps separate real signal changes from noise.
- How simulated data lets the analysis code be tested without hardware.
- How the test plan could be extended with oscilloscope or multimeter measurements.

## Next Features To Build

- Calibration command for known 0V and reference-voltage points.
- Multi-channel sampling for A0-A5.
- Live plot while logging.
- Auto-generated Markdown report after each capture.
