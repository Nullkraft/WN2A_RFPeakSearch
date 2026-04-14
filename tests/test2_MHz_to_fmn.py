import hardware_cfg as hw

name = "test2_MHz_to_fmn.py"

def test_MHz_to_fmn(ref_clock=67.10783):
    # Test case 1: check if valid F, M, and N values are returned for a given frequency
    frequency = 3000
    F_expected = 0x80B  # bits 31:20
    M_expected = 0xB6C  # bits 19:8
    N_expected = 0x2C   # bits 7:0
    assert hw.MHz_to_fmn(frequency, ref_clock) == (((F_expected << 20) | (M_expected << 8) | N_expected), frequency), "Test case 1: "

    # Test case 2: verify the current tuple return contract for a nearby frequency.
    frequency += 0.001
    assert hw.MHz_to_fmn(frequency, ref_clock) == (1640541484, frequency)
