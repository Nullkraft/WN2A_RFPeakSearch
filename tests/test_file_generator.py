import pytest
import hardware_cfg as hw

def test_MHz_to_fmn():
    # Test case 1: check if valid F, M, and N values are returned for a given frequency
    ref_clock = 66.0
    frequency = 0x12345678
    F_expected = 0x12345   # bits 31:20
    M_expected = 0x26      # bits 19:8
    N_expected = 0x78      # bits 7:0
    assert hw.MHz_to_fmn(frequency, ref_clock) == ((F_expected << 20) | (M_expected << 8) | N_expected)

    # Test case 2: check if value error is raised for N values between 0 and 15
    with pytest.raises(ValueError):
        hw.MHz_to_fmn(0x1234000F, ref_clock)

    # Test case 3: check if value error is raised for M values of 0 and 1
    with pytest.raises(ValueError):
        hw.MHz_to_fmn(0xFFFFFF00, ref_clock)
    with pytest.raises(ValueError):
        hw.MHz_to_fmn(0xFFFFF100, ref_clock)
