# Current Status

## Branch and Tag

- Active branch: `decoupling`
- Remote branch: `origin/decoupling`
- Preservation tag for the old threaded serial path: `serial_read_thread`

## Recent Committed Work

- `fdf6f29` `Decouple MainWindow from workflow logic`
  - Introduced `main_window_controller.py`
  - Moved startup/workflow orchestration out of `ui/mainWindow.py`
- `ed5b4d7` `Remove redundant control load log`
  - Removed duplicate startup sub-step logging from `application_interface.py`
- `c70269d` `Move peak marker preparation into controller`
  - Moved peak-search preparation behind `MainWindowController`
- `85f7050` `Add simulated peak search test`
  - Added `tests/test_peak_search.py`
- `746cfae` `Fix stale MHz_to_fmn test expectations`
  - Corrected `tests/test_file_generator.py` to match the current `hardware_cfg.MHz_to_fmn()` contract

## Current Uncommitted Change

- `ui/mainWindow.py`
  - Removed the dead `serial_read_thread()` path and the imports/helpers that only existed for it
  - This is intentionally not committed yet because hardware-backed testing has not been done

## Important Context

- The current sweep path is synchronous and runs through:
  - `MainWindow.on_btnSweep_clicked()`
  - `MainWindowController.run_sweep()`
  - `application_interface.sweep()`
  - `SA_Control.sweep()`
- The older threaded serial-read path was preserved before cleanup via the `serial_read_thread` tag because it may contain useful ideas for future RLE packet or progressive plotting work
- The old threaded path did not appear to be part of the active runtime path anymore, but hardware testing should confirm that before the cleanup is finalized

## Tests Checked Recently

- `python -m pytest -q tests/test_peak_search.py`
  - Passed
- `python -m pytest -q tests/test_file_generator.py`
  - Passed after correcting the stale test expectations

## Recommended Next Step

- Stop here until the hardware is connected and available
- Test the current `decoupling` branch against real hardware before continuing the decoupling effort
- Only after hardware verification decide whether to keep or revert the uncommitted `ui/mainWindow.py` serial cleanup

## Risks To Keep In Mind

- Further decoupling without hardware validation could break sweep behavior, serial timing, or device control paths in ways that static inspection will not catch
- `MainWindow` still has direct uses of `self.sa_ctl`; continuing decoupling should be done incrementally after confirming the existing hardware behavior is still correct
