# KEEP / MOVE / REMOVE PLAN

This is a working implementation checklist for the practical compromise architecture:

- `file_generator.py` owns planning, RF-model math, and precomputed sweep/control data.
- `spectrumAnalyzer.py` owns runtime sweep orchestration and ADC/sample association.
- `command_processor.py` owns Arduino protocol and command serialization.

Use this file for concrete decisions and implementation steps. Leave architectural notes in `KEEP_MOVE_REMOVE.md`.

## file_generator.py

### Keep Here

- [ ] Confirm `_compute_fmn_list()` remains in `file_generator.py`
- [ ] Confirm `DataGenerator._LO1_frequency_vectorized()` remains in `file_generator.py`
- [ ] Confirm `DataGenerator._LO2_frequency_vectorized()` remains in `file_generator.py`
- [ ] Confirm `DataGenerator._LO3_frequency()` remains in `file_generator.py`
- [ ] Confirm `DataGenerator._compute_fmn_serial()` remains in `file_generator.py`
- [ ] Confirm `DataGenerator._compute_fmn_parallel()` remains in `file_generator.py`
- [ ] Confirm `DataGenerator.create_data()` remains in `file_generator.py`
- [ ] Confirm `DataGenerator.save_ref1_hi_control_file()` remains in `file_generator.py`
- [ ] Confirm `DataGenerator.save_ref2_hi_control_file()` remains in `file_generator.py`
- [ ] Confirm `DataGenerator.save_ref1_lo_control_file()` remains in `file_generator.py`
- [ ] Confirm `DataGenerator.save_ref2_lo_control_file()` remains in `file_generator.py`

### Move Here Later

- [ ] Decide whether `fmn_to_MHz()` should move from `spectrumAnalyzer.py` into `file_generator.py` or a new planning helper module
- [ ] Decide whether `MHz_to_N()` should move from `spectrumAnalyzer.py` into `file_generator.py` or a new planning helper module
- [ ] Add a `build_sweep_step_table()` helper that emits one compact step record per requested sweep point
- [ ] Add a `choose_best_path_for_frequency()` helper that resolves calibration/control selection before sweep runtime
- [ ] Add an `emit_compact_step_payloads()` helper that prepares controller-facing step payloads ahead of the sweep

### Remove / Avoid Here

- [ ] Verify `file_generator.py` contains no serial writes
- [ ] Verify `file_generator.py` contains no device-select command words
- [ ] Verify `file_generator.py` contains no mux or power command semantics
- [ ] Verify `file_generator.py` contains no sweep-time lock/read timing logic

## spectrumAnalyzer.py

### Keep Here

- [ ] Confirm `SA_Control.get_control_codes()` remains in `spectrumAnalyzer.py`
- [ ] Confirm `SA_Control.adc_Vref()` remains in `spectrumAnalyzer.py`
- [ ] Confirm `SA_Control.get_x_range()` remains in `spectrumAnalyzer.py`
- [ ] Confirm `SA_Control.set_x_range()` remains in `spectrumAnalyzer.py`
- [ ] Confirm `SA_Control.create_LO3_sweep_list()` remains in `spectrumAnalyzer.py`
- [ ] Confirm `SA_Control.sweep_45()` remains in `spectrumAnalyzer.py`
- [ ] Confirm `SA_Control.sweep_315()` remains in `spectrumAnalyzer.py`
- [ ] Confirm `SA_Control.sweep()` remains in `spectrumAnalyzer.py`

### Keep Here For Now, Narrow Later

- [ ] Review `SA_Control.set_reference_clock()` and remove chip-identity language while keeping orchestration behavior
- [ ] Review `SA_Control.set_attenuator()` and remove chip-identity language while keeping orchestration behavior
- [ ] Review `SA_Control.set_LO1()` and remove chip-identity language while keeping orchestration behavior
- [ ] Review `SA_Control.set_LO2()` and remove chip-identity language while keeping orchestration behavior
- [ ] Review `SA_Control.set_LO3()` and remove chip-identity language while keeping orchestration behavior

### Move Later

- [ ] Move `peakSearch()` from `spectrumAnalyzer.py` into a plotting or analysis module
- [ ] Move `is_peak()` from `spectrumAnalyzer.py` into a plotting or analysis module
- [ ] Move `fmn_to_MHz()` from `spectrumAnalyzer.py` into the planning/model layer
- [ ] Move `MHz_to_N()` from `spectrumAnalyzer.py` into the planning/model layer

### Remove / Replace Later

- [ ] Decide whether chip-shaped wrapper names should be replaced with step-oriented names such as `apply_lo1_step()`
- [ ] Add an explicit sweep-time alignment check between `swept_freq_list` length and returned ADC pair count
- [ ] Remove chip identity assumptions from sweep orchestration comments and docstrings

## command_processor.py

### Keep Here

- [ ] Confirm `CommandProcessor._send_command()` remains in `command_processor.py`
- [ ] Confirm `CommandProcessor.show_message()` remains in `command_processor.py`
- [ ] Confirm `CommandProcessor.get_version_message()` remains in `command_processor.py`
- [ ] Confirm `CommandProcessor.end_sweep()` remains in `command_processor.py`
- [ ] Confirm `CommandProcessor.set_attenuator()` remains in `command_processor.py`
- [ ] Confirm `CommandProcessor.enable_ref_clock()` remains in `command_processor.py`
- [ ] Confirm `CommandProcessor.disable_all_ref_clocks()` remains in `command_processor.py`

### Keep Here For Now, Rename / Rescope Later

- [ ] Decide whether `CommandProcessor.sel_LO1()` stays public or is renamed to a protocol-oriented helper
- [ ] Decide whether `CommandProcessor.set_LO1()` stays public or is renamed to a protocol-oriented helper
- [ ] Decide whether `CommandProcessor.sel_LO2()` stays public or is renamed to a protocol-oriented helper
- [ ] Decide whether `CommandProcessor.set_LO2()` stays public or is renamed to a protocol-oriented helper
- [ ] Decide whether `CommandProcessor.sel_LO3()` stays public or is renamed to a protocol-oriented helper
- [ ] Decide whether `CommandProcessor.set_LO3()` stays public or is renamed to a protocol-oriented helper
- [ ] Decide whether `CommandProcessor.disable_LO2_RFout()` should be kept as-is or renamed as protocol behavior
- [ ] Decide whether `CommandProcessor.disable_LO3_RFout()` should be kept as-is or renamed as protocol behavior
- [ ] Decide whether `CommandProcessor.LO_device_register()` should be kept, renamed, or removed
- [ ] Decide whether `CommandProcessor.set_max2871_freq()` is still required by direct-programming workflows

### Replace Later

- [ ] Define whether `send_reference_command()` should replace the current reference-facing public API
- [ ] Define whether `send_lo1_payload()` should replace the current LO1-facing public API
- [ ] Define whether `send_lo2_payload()` should replace the current LO2-facing public API
- [ ] Define whether `send_lo3_payload()` should replace the current LO3-facing public API
- [ ] Define whether `send_mode_command()` should replace the current mode-setting public API
- [ ] Define whether `send_sweep_end()` should replace the current sweep-end public API

### Remove / Avoid Here

- [ ] Verify `command_processor.py` contains no frequency-planning math
- [ ] Verify `command_processor.py` contains no calibration decision logic
- [ ] Verify `command_processor.py` contains no plot/sweep ordering logic

## Cross-Module Steps

- [ ] Define the minimum controller-facing sweep-step payload the PC should send for one sweep point
- [ ] Decide which payload fields are computed offline and which must be computed at sweep runtime
- [ ] List the chip-specific Python-facing API terms that can be removed without breaking the Arduino protocol
- [ ] List any direct-programming or debug paths that still require chip-specific naming
- [ ] Run a sweep and compare `len(swept_freq_list)` to returned ADC pair count in `sweep_controls.csv`
- [ ] Run a representative sweep and confirm precomputed step data preserves sweep speed
