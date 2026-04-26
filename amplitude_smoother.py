#!/usr/bin/env python3
"""Smooth the four calibration amplitude files with the repo's moving average.

This script loads the four default calibration arrays:

    amplitude_ref1_HI.npy
    amplitude_ref1_LO.npy
    amplitude_ref2_HI.npy
    amplitude_ref2_LO.npy

It applies the same centered moving-average smoothing used by
application_interface.make_control_dictionary(), then writes four output .npy
files. By default, the output names append a suffix before `.npy`.
"""

import argparse
from pathlib import Path

import numpy as np


DEFAULT_INPUTS = (
    "amplitude_ref1_HI.npy",
    "amplitude_ref1_LO.npy",
    "amplitude_ref2_HI.npy",
    "amplitude_ref2_LO.npy",
)


def smooth_values(values, half_window):
    """Apply the repo's centered moving average and round to 3 decimals."""
    smoothed = []
    length = len(values)
    for idx in range(length):
        start = max(0, idx - half_window)
        stop = min(length, idx + half_window)
        smoothed.append(round(float(np.average(values[start:stop])), 3))
    return np.array(smoothed, dtype=np.float32)


def default_output_path(input_path, suffix):
    return input_path.with_name("{}{}{}".format(input_path.stem, suffix, input_path.suffix))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Smooth the four calibration amplitude .npy files and write smoothed .npy outputs."
    )
    parser.add_argument(
        "half_window",
        type=int,
        help="Half-window used by the centered moving average.",
    )
    parser.add_argument(
        "--suffix",
        default="_smoothed",
        help="Suffix inserted before .npy when output paths are not specified (default: _smoothed).",
    )
    parser.add_argument("--a1-in", default=DEFAULT_INPUTS[0], help="Input file for A1 (default: amplitude_ref1_HI.npy).")
    parser.add_argument("--a2-in", default=DEFAULT_INPUTS[1], help="Input file for A2 (default: amplitude_ref1_LO.npy).")
    parser.add_argument("--a3-in", default=DEFAULT_INPUTS[2], help="Input file for A3 (default: amplitude_ref2_HI.npy).")
    parser.add_argument("--a4-in", default=DEFAULT_INPUTS[3], help="Input file for A4 (default: amplitude_ref2_LO.npy).")
    parser.add_argument("--a1-out", help="Explicit output path for A1.")
    parser.add_argument("--a2-out", help="Explicit output path for A2.")
    parser.add_argument("--a3-out", help="Explicit output path for A3.")
    parser.add_argument("--a4-out", help="Explicit output path for A4.")
    return parser.parse_args()


def main():
    args = parse_args()

    input_paths = [
        Path(args.a1_in),
        Path(args.a2_in),
        Path(args.a3_in),
        Path(args.a4_in),
    ]
    output_paths = [
        Path(args.a1_out) if args.a1_out else default_output_path(input_paths[0], args.suffix),
        Path(args.a2_out) if args.a2_out else default_output_path(input_paths[1], args.suffix),
        Path(args.a3_out) if args.a3_out else default_output_path(input_paths[2], args.suffix),
        Path(args.a4_out) if args.a4_out else default_output_path(input_paths[3], args.suffix),
    ]

    loaded = [np.load(path, allow_pickle=False) for path in input_paths]
    lengths = {len(arr) for arr in loaded}
    if len(lengths) != 1:
        raise ValueError("All inputs must have the same length, got lengths: {}".format(sorted(lengths)))

    for input_path, output_path, values in zip(input_paths, output_paths, loaded):
        smoothed = smooth_values(values, args.half_window)
        np.save(output_path, smoothed)
        print("{} -> {} ({} values)".format(input_path, output_path, len(smoothed)))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
