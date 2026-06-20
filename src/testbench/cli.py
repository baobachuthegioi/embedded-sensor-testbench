from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import read_samples, validate_run
from .serial_logger import log_serial
from .simulate import generate_samples, write_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sensor-testbench",
        description="Capture, simulate, and analyze Arduino sensor testbench data.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    simulate_parser = subparsers.add_parser("simulate", help="Generate a repeatable sample run")
    simulate_parser.add_argument("--samples", type=int, default=250)
    simulate_parser.add_argument("--output", default="data/demo_run.csv")
    simulate_parser.add_argument("--seed", type=int, default=42)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a CSV run")
    analyze_parser.add_argument("csv_path")
    analyze_parser.add_argument("--max-noise-pp-mv", type=float, default=1500.0)
    analyze_parser.add_argument("--max-outlier-ratio", type=float, default=0.03)

    log_parser = subparsers.add_parser("log", help="Log a hardware run from serial")
    log_parser.add_argument("--port", required=True)
    log_parser.add_argument("--seconds", type=float, default=30.0)
    log_parser.add_argument("--baud", type=int, default=115200)
    log_parser.add_argument("--output", default="data/hardware_run.csv")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "simulate":
        rows = generate_samples(samples=args.samples, seed=args.seed)
        write_csv(rows, args.output)
        print(f"Wrote {len(rows)} samples to {Path(args.output)}")
        return 0

    if args.command == "analyze":
        samples = read_samples(args.csv_path)
        result = validate_run(
            samples,
            max_noise_pp_mv=args.max_noise_pp_mv,
            max_outlier_ratio=args.max_outlier_ratio,
        )
        _print_result(result)
        return 0 if result["passed"] else 2

    if args.command == "log":
        lines = log_serial(args.port, args.seconds, args.output, baud=args.baud)
        print(f"Wrote {lines} serial lines to {Path(args.output)}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


def _print_result(result: dict[str, object]) -> None:
    summary = result["summary"]
    assert isinstance(summary, dict)

    print(f"Samples: {summary['sample_count']}")
    print(f"Duration: {summary['duration_ms']} ms")
    print(
        "Voltage avg/min/max: "
        f"{summary['voltage_avg_mv']:.1f} / "
        f"{summary['voltage_min_mv']:.1f} / "
        f"{summary['voltage_max_mv']:.1f} mV"
    )
    print(f"Peak-to-peak noise: {summary['noise_pp_mv']:.1f} mV")
    print(f"RMS noise: {summary['noise_rms_mv']:.1f} mV")
    print(f"Outlier ratio: {result['outlier_ratio']:.2%}")

    if result["passed"]:
        print("Verdict: PASS")
        return

    print("Verdict: FAIL")
    for failure in result["failures"]:
        print(f"- {failure}")
