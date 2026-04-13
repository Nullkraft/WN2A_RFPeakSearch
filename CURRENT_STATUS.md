# Current Status

## Branch and Tag

- Active branch: `decoupling`
- Remote branch: `origin/decoupling`
- Branch tip: `1afe84c` `Remove stale serial thread path`
- Preservation tag for the old threaded serial path: `serial_read_thread`

## Recent Committed Work

- `1afe84c` `Remove stale serial thread path`
  - Removed the unused `serial_read_thread()` path and related helpers/imports from `ui/mainWindow.py`
  - Added this status file to capture the current decoupling state before hardware validation
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

## Current Working Tree

- No tracked project files are modified
- The only untracked path is `.codex`

## Important Context

- The current sweep path is synchronous and runs through:
  - `MainWindow.on_btnSweep_clicked()`
  - `MainWindowController.run_sweep()`
  - `application_interface.sweep()`
  - `SA_Control.sweep()`
- The older threaded serial-read path was preserved before cleanup via the `serial_read_thread` tag because it may contain useful ideas for future RLE packet or progressive plotting work
- The old threaded path did not appear to be part of the active runtime path anymore, but hardware testing should still confirm that the committed cleanup was safe

## Tests Checked Recently

- `source bin/activate && python -m pytest -q tests/test_peak_search.py`
  - Passed
- `source bin/activate && python -m pytest -q tests/test_file_generator.py`
  - Passed after correcting the stale test expectations
- `python3 -m py_compile ui/mainWindow.py`
  - Passed during the serial-thread cleanup

## Recommended Next Step

- Stop here until the hardware is connected and available
- Test the current `decoupling` branch against real hardware before continuing the decoupling effort
- Focus first on sweep behavior, serial timing, and end-to-end device control on real hardware
- Only after hardware verification continue reducing direct `self.sa_ctl` usage inside `MainWindow`

## Risks To Keep In Mind

- Further decoupling without hardware validation could break sweep behavior, serial timing, or device control paths in ways that static inspection will not catch
- `MainWindow` still has direct uses of `self.sa_ctl`; continuing decoupling should be done incrementally after confirming the existing hardware behavior is still correct
