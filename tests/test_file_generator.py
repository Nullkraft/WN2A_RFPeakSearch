import hardware_cfg as hw

def test_MHz_to_fmn():
    # Test case 1: check the current tuple return contract for a valid frequency.
    ref_clock = 66.0
    frequency = 3000.0
    fmn_expected = 1951398957
    fmn_word, fvco = hw.MHz_to_fmn(frequency, ref_clock)
    assert fmn_word == fmn_expected
    assert fvco == frequency

    # Test case 2: verify a second reference clock still returns the tuple form.
    ref_clock = 67.108864
    fmn_word, fvco = hw.MHz_to_fmn(frequency, ref_clock)
    assert fmn_word == 2732488492
    assert fvco == frequency
