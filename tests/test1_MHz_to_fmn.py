import hardware_cfg as hw

name = "test1_MHz_to_fmn.py"

def test_MHz_to_fmn(ref_clock=65.99936):
    # Test case 1: check if valid F, M, and N values are returned for a given frequency
    frequency = 3000
    F_expected = 0x291  # bits 31:20
    M_expected = 0x5A4  # bits 19:8
    N_expected = 0x2D   # bits 7:0
    assert hw.MHz_to_fmn(frequency, ref_clock) == (((F_expected << 20) | (M_expected << 8) | N_expected), frequency)

    # Test case 2: verify the current tuple return contract for a nearby frequency.
    frequency += 0.001
    assert hw.MHz_to_fmn(frequency, ref_clock) == (1713243437, frequency)
