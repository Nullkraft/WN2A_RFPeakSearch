import pytest
import hardware_cfg as hw

name = "test2_MHz_to_fmn.py"

def test_MHz_to_fmn(ref_clock=67.108864):
    # Test case 1: check if valid F, M, and N values are returned for a given frequency
    frequency = 3000
    F_expected = 0xA2D  # bits 31:20
    M_expected = 0xE77  # bits 19:8
    N_expected = 0x2C   # bits 7:0
    assert hw.MHz_to_fmn(frequency, ref_clock) == ((F_expected << 20) | (M_expected << 8) | N_expected), "Test case 1: "

    #Test case 2: check if value error is raised for RFin == 3000.001 MHz when ref_clock == 66.0 MHz
    frequency += 0.001
    #Test case 2: check if value error is raised for RFin == 3000.001 MHz when ref_clock == 67.108864 MHz
    with pytest.raises(ValueError):
        assert hw.MHz_to_fmn(frequency, ref_clock) == 2732488492    #, f"{name}: FMN value doesn't match"
