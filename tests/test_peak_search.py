import importlib
import random
import sys
import types


class _DummyListener:
    def __init__(self, *args, **kwargs):
        pass

    def start(self):
        return None


keyboard_module = types.ModuleType("pynput.keyboard")
keyboard_module.Listener = _DummyListener
keyboard_module.Key = types.SimpleNamespace(esc="esc")

pynput_module = types.ModuleType("pynput")
pynput_module.keyboard = keyboard_module

sys.modules["pynput"] = pynput_module
sys.modules["pynput.keyboard"] = keyboard_module

sa = importlib.import_module("spectrumAnalyzer")


def simulate_adc_amplitudes(num_points=1600, num_peaks=3, seed=42):
    rng = random.Random(seed)
    amplitudes = [rng.randint(20, 120) for _ in range(num_points)]
    peak_positions = []
    peak_heights = {}

    while len(peak_positions) < num_peaks:
        pos = rng.randint(10, num_points - 11)
        if all(abs(pos - existing) > 80 for existing in peak_positions):
            peak_positions.append(pos)

    for pos in peak_positions:
        peak = rng.randint(700, 1023)
        left = rng.randint(80, min(peak - 40, 500))
        right = rng.randint(80, min(peak - 40, 500))
        amplitudes[pos - 1] = left
        amplitudes[pos] = peak
        amplitudes[pos + 1] = right
        peak_heights[pos] = peak

    expected = sorted(peak_positions, key=lambda pos: peak_heights[pos], reverse=True)
    return amplitudes, expected


def test_peak_search_finds_three_random_adc_peaks():
    amplitudes, expected = simulate_adc_amplitudes()
    found = sa.peakSearch(amplitudes, 3)
    assert len(amplitudes) == 1600
    assert min(amplitudes) >= 0
    assert max(amplitudes) <= 1023
    assert found[:3] == expected
