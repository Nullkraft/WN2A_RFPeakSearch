# KEEP / MOVE / REMOVE

This is a working checklist for the practical compromise architecture:

- `file_generator.py` owns planning, RF-model math, and precomputed sweep/control data.
- `spectrumAnalyzer.py` owns runtime sweep orchestration and ADC/sample association.
- `command_processor.py` owns Arduino protocol and command serialization.

## file_generator.py

### Keep Here

- Keep `_compute_fmn_list()`
- Keep `DataGenerator._LO1_frequency_vectorized()`
- Keep `DataGenerator._LO2_frequency_vectorized()`
- Keep `DataGenerator._LO3_frequency()`
- Keep `DataGenerator._compute_fmn_serial()`
- Keep `DataGenerator._compute_fmn_parallel()`
- Keep `DataGenerator.create_data()`
- Keep `DataGenerator.save_ref1_hi_control_file()`
- Keep `DataGenerator.save_ref2_hi_control_file()`
- Keep `DataGenerator.save_ref1_lo_control_file()`
- Keep `DataGenerator.save_ref2_lo_control_file()`

### Move Here Later

- Move `fmn_to_MHz()` from `spectrumAnalyzer.py` into the planning/model layer
- Move `MHz_to_N()` from `spectrumAnalyzer.py` into the planning/model layer
- Add a `build_sweep_step_table()` helper for compact runtime step generation
- Add a `choose_best_path_for_frequency()` helper for calibration/control selection
- Add a `emit_compact_step_payloads()` helper for controller-facing precomputed sweep data

### Remove / Avoid Here

- Keep serial writes out of `file_generator.py`
- Keep device-select command words out of `file_generator.py`
- Keep mux/power command semantics out of `file_generator.py`
- Keep sweep-time lock/read timing out of `file_generator.py`

## spectrumAnalyzer.py

### Keep Here

- Keep `SA_Control.get_control_codes()`
- Keep `SA_Control.adc_Vref()`
- Keep `SA_Control.get_x_range()`
- Keep `SA_Control.set_x_range()`
- Keep `SA_Control.create_LO3_sweep_list()`
- Keep `SA_Control.sweep_45()`
- Keep `SA_Control.sweep_315()`
- Keep `SA_Control.sweep()`

### Keep Here For Now, Narrow Later

- Keep `SA_Control.set_reference_clock()` as an orchestration wrapper, but narrow chip-specific assumptions
- Keep `SA_Control.set_attenuator()` as an orchestration wrapper, but narrow chip-specific assumptions
- Keep `SA_Control.set_LO1()` as an orchestration wrapper, but narrow chip-specific assumptions
- Keep `SA_Control.set_LO2()` as an orchestration wrapper, but narrow chip-specific assumptions
- Keep `SA_Control.set_LO3()` as an orchestration wrapper, but narrow chip-specific assumptions

### Move Later

- Move `peakSearch()` out of `spectrumAnalyzer.py` into a plotting/analysis module
- Move `is_peak()` out of `spectrumAnalyzer.py` into a plotting/analysis module
- Move `fmn_to_MHz()` out of `spectrumAnalyzer.py` into the planning/model layer
- Move `MHz_to_N()` out of `spectrumAnalyzer.py` into the planning/model layer

### Remove / Replace Later

- Replace direct chip-shaped wrapper naming with step-oriented names where practical
- Replace implicit frequency-to-sample alignment assumptions with explicit alignment checks where practical
- Remove chip identity assumptions from sweep orchestration where practical

## command_processor.py

### Keep Here

- Keep `CommandProcessor._send_command()`
- Keep `CommandProcessor.show_message()`
- Keep `CommandProcessor.get_version_message()`
- Keep `CommandProcessor.end_sweep()`
- Keep `CommandProcessor.set_attenuator()`
- Keep `CommandProcessor.enable_ref_clock()`
- Keep `CommandProcessor.disable_all_ref_clocks()`

### Keep Here For Now, Rename / Rescope Later

- Keep `CommandProcessor.sel_LO1()` for now, but treat it as controller protocol rather than chip identity
- Keep `CommandProcessor.set_LO1()` for now, but treat it as controller protocol rather than chip identity
- Keep `CommandProcessor.sel_LO2()` for now, but treat it as controller protocol rather than chip identity
- Keep `CommandProcessor.set_LO2()` for now, but treat it as controller protocol rather than chip identity
- Keep `CommandProcessor.sel_LO3()` for now, but treat it as controller protocol rather than chip identity
- Keep `CommandProcessor.set_LO3()` for now, but treat it as controller protocol rather than chip identity
- Keep `CommandProcessor.disable_LO2_RFout()` for now, but rescope as protocol behavior
- Keep `CommandProcessor.disable_LO3_RFout()` for now, but rescope as protocol behavior
- Keep `CommandProcessor.LO_device_register()` for now, but rescope or replace with clearer protocol naming
- Keep `CommandProcessor.set_max2871_freq()` only if still needed by direct-programming workflows

### Replace Later

- Replace chip-specific public API names with protocol-oriented names such as `send_reference_command()`
- Replace chip-specific public API names with protocol-oriented names such as `send_lo1_payload()`
- Replace chip-specific public API names with protocol-oriented names such as `send_lo2_payload()`
- Replace chip-specific public API names with protocol-oriented names such as `send_lo3_payload()`
- Replace chip-specific public API names with protocol-oriented names such as `send_mode_command()`
- Replace chip-specific public API names with protocol-oriented names such as `send_sweep_end()`

### Remove / Avoid Here

- Avoid frequency-planning math in `command_processor.py`
- Avoid calibration decision logic in `command_processor.py`
- Avoid plot/sweep ordering logic in `command_processor.py`

## Cross-Module Steps

- Define the minimum controller-facing sweep-step payload the PC should send
- Decide which fields are computed offline versus at sweep runtime
- Decide which chip-specific terms can be removed from Python-facing APIs without breaking the Arduino protocol
- Identify any direct-programming/debug paths that still require chip-specific naming
- Confirm the ADC return stream remains one sample per requested `swept_freq_list` entry
- Confirm sweep-step precomputation reduces controller-side work enough to preserve sweep speed
