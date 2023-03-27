import pytest
import hardware_cfg as hw

name = "test1_MHz_to_fmn.py"

def test_MHz_to_fmn(ref_clock=66.0):
    # Test case 1: check if valid F, M, and N values are returned for a given frequency
    frequency = 3000
    F_expected = 0x744  # bits 31:20
    M_expected = 0xFFC  # bits 19:8
    N_expected = 0x2D   # bits 7:0
    assert hw.MHz_to_fmn(frequency, ref_clock) == ((F_expected << 20) | (M_expected << 8) | N_expected)

    #Test case 2: check if value error is raised for RFin == 3000.001 MHz when ref_clock == 66.0 MHz
    frequency += 0.001
    with pytest.raises(ValueError):
        assert hw.MHz_to_fmn(frequency, ref_clock) == 1951398957    #, f"{name}: FMN value doesn't match"

