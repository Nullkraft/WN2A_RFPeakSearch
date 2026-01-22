# -*- coding: utf-8 -*-
#
# This file is part of WN2A_RFPeakSearch.
#
# This file is part of the WN2A_RFPeakSearch distribution (https://github.com/Nullkraft/WN2A_RFPeakSearch).
# Copyright (c) 2021 Mark Stanley.
#
# WN2A_RFPeakSearch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# WN2A_RFPeakSearch is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
NPY Viewer - Utility for viewing spectrum analyzer control files.

Usage examples:
    # Show file info and first/last rows
    python npy_viewer.py control_ref1_HI.npy

    # Display specific frequency
    python npy_viewer.py control_ref1_HI.npy --freq 1500.0

    # Display frequency range
    python npy_viewer.py control_ref1_HI.npy --range 1000.0 1010.0

    # Compare two files
    python npy_viewer.py control_ref1_HI.npy --compare control_ref2_HI.npy

    # Export slice to CSV
    python npy_viewer.py control_ref1_HI.npy --range 100.0 200.0 --export slice.csv
"""

import argparse
import numpy as np
import sys
from pathlib import Path


# Constants matching file_generator.py
NUM_FREQUENCIES = 3_000_001
FREQ_STEP_KHZ = 0.001  # 1 kHz steps
MAX_FREQ_MHZ = 3000.0

# Reference clock control code mapping
REF_CLOCK_MAP = {
    3327: 1,  # ref_clock1_enable
    5375: 2,  # ref_clock2_enable
}


def map_ref_clock(value: int) -> str:
    """Map control code to ref_clock display value."""
    return str(REF_CLOCK_MAP.get(value, value))


def freq_to_index(freq_mhz: float) -> int:
    """Convert frequency in MHz to array index."""
    index = int(round(freq_mhz / FREQ_STEP_KHZ))
    return max(0, min(index, NUM_FREQUENCIES - 1))


def index_to_freq(index: int) -> float:
    """Convert array index to frequency in MHz."""
    return index * FREQ_STEP_KHZ


def load_control_file(filepath: str) -> np.ndarray:
    """Load an npy control file and validate its shape."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    data = np.load(filepath)

    if data.shape[1] != 3:
        print(f"Error: Expected 3 columns, got {data.shape[1]}")
        sys.exit(1)

    return data


def format_row(index: int, row: np.ndarray, hex_output: bool = True) -> str:
    """Format a single row for display."""
    freq = index_to_freq(index)
    ref_ctrl, lo1_n, lo2_fmn = row
    ref_clock = map_ref_clock(ref_ctrl)

    if hex_output:
        return f"{freq:12.3f}    {ref_clock:>9}    {lo1_n:>8}    0x{lo2_fmn:08X}"
    else:
        return f"{freq:12.3f}    {ref_clock:>9}    {lo1_n:>8}    {lo2_fmn:>12}"


def print_header(hex_output: bool = True) -> None:
    """Print the column header."""
    if hex_output:
        print(f"{'RFin(MHz)':>12}    {'ref_clock':>9}    {'LO1_N':>8}    {'LO2_FMN':>12}")
    else:
        print(f"{'RFin(MHz)':>12}    {'ref_clock':>9}    {'LO1_N':>8}    {'LO2_FMN':>12}")
    print("─" * 57)


def print_file_info(filepath: str, data: np.ndarray) -> None:
    """Print file metadata."""
    print(f"\nFile: {filepath}")
    print(f"Shape: {data.shape}")
    print(f"Dtype: {data.dtype}")
    print(f"Frequency range: 0.000 - {MAX_FREQ_MHZ:.3f} MHz")
    print(f"Frequency step: {FREQ_STEP_KHZ * 1000:.0f} kHz")
    print()


def display_summary(data: np.ndarray, num_rows: int = 5) -> None:
    """Display first and last rows of the data."""
    print_header()

    # First rows
    for i in range(num_rows):
        print(format_row(i, data[i]))

    print(f"{'...':>12}    {'...':>9}    {'...':>8}    {'...':>12}")

    # Last rows
    for i in range(NUM_FREQUENCIES - num_rows, NUM_FREQUENCIES):
        print(format_row(i, data[i]))

    print(f"\nShowing rows 0-{num_rows-1} and {NUM_FREQUENCIES-num_rows}-{NUM_FREQUENCIES-1} of {NUM_FREQUENCIES}")


def display_frequency(data: np.ndarray, freq_mhz: float) -> None:
    """Display data for a specific frequency."""
    index = freq_to_index(freq_mhz)
    actual_freq = index_to_freq(index)

    if abs(actual_freq - freq_mhz) > FREQ_STEP_KHZ / 2:
        print(f"Note: Requested {freq_mhz:.3f} MHz, showing nearest: {actual_freq:.3f} MHz")

    print_header()
    print(format_row(index, data[index]))


def display_range(data: np.ndarray, start_mhz: float, end_mhz: float, max_display: int = 100) -> None:
    """Display data for a frequency range."""
    start_idx = freq_to_index(start_mhz)
    end_idx = freq_to_index(end_mhz)

    if start_idx > end_idx:
        start_idx, end_idx = end_idx, start_idx

    num_rows = end_idx - start_idx + 1

    print(f"Range: {index_to_freq(start_idx):.3f} - {index_to_freq(end_idx):.3f} MHz ({num_rows} points)")
    print()
    print_header()

    if num_rows <= max_display:
        for i in range(start_idx, end_idx + 1):
            print(format_row(i, data[i]))
    else:
        # Show first half and last half
        half = max_display // 2
        for i in range(start_idx, start_idx + half):
            print(format_row(i, data[i]))

        print(f"{'...':>12}    {'...':>9}    {'...':>8}    {'...':>12}")
        print(f"    ({num_rows - max_display} rows omitted)")
        print(f"{'...':>12}    {'...':>9}    {'...':>8}    {'...':>12}")

        for i in range(end_idx - half + 1, end_idx + 1):
            print(format_row(i, data[i]))


def compare_files(file1: str, file2: str, start_mhz: float = None, end_mhz: float = None, max_display: int = 50) -> None:
    """Compare two control files side-by-side."""
    data1 = load_control_file(file1)
    data2 = load_control_file(file2)

    name1 = Path(file1).stem
    name2 = Path(file2).stem

    if start_mhz is None:
        start_mhz = 0.0
    if end_mhz is None:
        end_mhz = MAX_FREQ_MHZ

    start_idx = freq_to_index(start_mhz)
    end_idx = freq_to_index(end_mhz)
    num_rows = end_idx - start_idx + 1

    print(f"\nComparing: {file1} vs {file2}")
    print(f"Range: {index_to_freq(start_idx):.3f} - {index_to_freq(end_idx):.3f} MHz ({num_rows} points)")
    print()

    # Find differences
    diff_mask = np.any(data1[start_idx:end_idx+1] != data2[start_idx:end_idx+1], axis=1)
    diff_indices = np.where(diff_mask)[0] + start_idx
    num_diffs = len(diff_indices)

    print(f"Differences found: {num_diffs} rows ({100*num_diffs/num_rows:.2f}%)")
    print()

    if num_diffs == 0:
        print("Files are identical in the specified range.")
        return

    # Print header for comparison
    print(f"{'RFin(MHz)':>12}    {'─── ' + name1 + ' ───':<36}    {'─── ' + name2 + ' ───':<36}")
    print(f"{'':>12}    {'ref_clock':>9} {'LO1_N':>8} {'LO2_FMN':>12}    {'ref_clock':>9} {'LO1_N':>8} {'LO2_FMN':>12}")
    print("─" * 100)

    # Display differences (limited)
    display_count = min(num_diffs, max_display)
    for i, idx in enumerate(diff_indices[:display_count]):
        freq = index_to_freq(idx)
        r1 = data1[idx]
        r2 = data2[idx]
        ref1 = map_ref_clock(r1[0])
        ref2 = map_ref_clock(r2[0])

        line = f"{freq:12.3f}    {ref1:>9} {r1[1]:>8} 0x{r1[2]:08X}    {ref2:>9} {r2[1]:>8} 0x{r2[2]:08X}"

        # Mark which columns differ
        markers = []
        if r1[0] != r2[0]:
            markers.append("ref_clock")
        if r1[1] != r2[1]:
            markers.append("LO1")
        if r1[2] != r2[2]:
            markers.append("FMN")

        print(f"{line}  <- {','.join(markers)}")

    if num_diffs > max_display:
        print(f"\n... and {num_diffs - max_display} more differences")


def export_to_csv(data: np.ndarray, output_file: str, start_mhz: float = None, end_mhz: float = None) -> None:
    """Export a slice of data to CSV format."""
    if start_mhz is None:
        start_mhz = 0.0
    if end_mhz is None:
        end_mhz = MAX_FREQ_MHZ

    start_idx = freq_to_index(start_mhz)
    end_idx = freq_to_index(end_mhz)

    with open(output_file, 'w') as f:
        f.write("RFin_MHz,ref_clock,LO1_N,LO2_FMN_hex,LO2_FMN_dec\n")

        for i in range(start_idx, end_idx + 1):
            freq = index_to_freq(i)
            ref_ctrl, lo1_n, lo2_fmn = data[i]
            ref_clock = map_ref_clock(ref_ctrl)
            f.write(f"{freq:.3f},{ref_clock},{lo1_n},0x{lo2_fmn:08X},{lo2_fmn}\n")

    num_rows = end_idx - start_idx + 1
    print(f"Exported {num_rows} rows to {output_file}")
    print(f"Range: {index_to_freq(start_idx):.3f} - {index_to_freq(end_idx):.3f} MHz")


EXAMPLES = """Examples:
  npy_viewer.py control_ref1_HI.npy                        Show file summary
  npy_viewer.py control_ref1_HI.npy --freq 1500.0          Show data at 1500 MHz
  npy_viewer.py control_ref1_HI.npy --range 1000 1010      Show 1000-1010 MHz range
  npy_viewer.py control_ref1_HI.npy --compare ref2.npy     Compare two files
  npy_viewer.py control_ref1_HI.npy -r 100 200 -e out.csv  Export range to CSV"""


class HelpfulArgumentParser(argparse.ArgumentParser):
    """Custom parser that shows usage and examples on error."""
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"{EXAMPLES}\n")
        sys.stderr.write(f"{self.prog}: error: {message}\n")
        sys.exit(2)


def main():
    parser = HelpfulArgumentParser(
        description="View and analyze spectrum analyzer control files (.npy)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXAMPLES
    )

    parser.add_argument("file", help="Input .npy control file")
    parser.add_argument("-f", "--freq", type=float, metavar="MHZ",
                        help="Display data for specific frequency (MHz)")
    parser.add_argument("-r", "--range", type=float, nargs=2, metavar=("START", "END"),
                        help="Display frequency range (MHz)")
    parser.add_argument("-c", "--compare", metavar="FILE2",
                        help="Compare with another .npy file")
    parser.add_argument("-e", "--export", metavar="OUTPUT.CSV",
                        help="Export to CSV file")
    parser.add_argument("-d", "--decimal", action="store_true",
                        help="Show FMN values in decimal instead of hex")
    parser.add_argument("-n", "--num-rows", type=int, default=50,
                        help="Max rows to display (default: 50)")

    args = parser.parse_args()

    # Load primary file
    data = load_control_file(args.file)
    print_file_info(args.file, data)

    # Handle export
    if args.export:
        start = args.range[0] if args.range else None
        end = args.range[1] if args.range else None
        export_to_csv(data, args.export, start, end)
        return

    # Handle compare
    if args.compare:
        start = args.range[0] if args.range else None
        end = args.range[1] if args.range else None
        compare_files(args.file, args.compare, start, end, args.num_rows)
        return

    # Handle frequency or range display
    if args.freq is not None:
        display_frequency(data, args.freq)
    elif args.range:
        display_range(data, args.range[0], args.range[1], args.num_rows)
    else:
        display_summary(data)


if __name__ == "__main__":
    main()
