import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import sys
from hardware_cfg import MHz_to_fmn
from time import perf_counter
from os import cpu_count
from typing import Optional

line = lambda: f"line {str(sys._getframe(1).f_lineno)},"    # Report which line in the file

R = 2
ref_clock = 66.000
Fpfd = ref_clock / R


def fmn_to_MHz(fmn_word, Fpfd, show_fmn: bool=False):
  F_ = fmn_word >> 20
  M_= (fmn_word & 0xFFFFF) >> 8
  if M_ == 0:
      M_ = 2
  N_ = fmn_word & 0xFF
  if show_fmn:
      print('\t', f'M:F:N = {M_.item(),F_.item(),N_.item()}')
  freq_MHz = Fpfd * (N_ + F_/M_)
  return freq_MHz


def np_MHz_to_fmn(target_freqs: np.ndarray, M: np.ndarray, Fpfd: float=66.0):
  global F_list
  global diffs
  """ Form a 32 bit word consisting of 12 bits of F, 12 bits of M and 8 bits of N for the MAX2871. """
  div = 2**np.arange(8)                           # Create 8 Fpfd multipliers ...
  Fvco = div * target_freqs[:, None]              # ... to reach Fvco = (vco => 3000 MHz)
  div_mask = Fvco >= 3000                         # table of True/False: Which of the 8 are >3000?
  indices = np.argmax(div_mask, axis=1)[:, None]  # Using indices for Fvco masking
  Fvco = np.take_along_axis(Fvco, indices, axis=1)# Done with indicies, now it can be used elsewhere
  step_fract, N = np.modf(Fvco/Fpfd)
  N = N.astype(np.int16)
#  N = (Fvco/Fpfd).astype(np.int16)                 # Integer portion of the step size for register N
#  step_fract = Fvco/Fpfd - N                       # Fractional portion of the step size
  F = (M * step_fract).astype(np.int64)            # Convert decimal part for register F
  Fvco_diffs = np.abs(Fvco - (Fpfd * (N + F/M)))
  indices = np.argmin(Fvco_diffs, axis=1)[:, None] # Get the index of the minimum error ....
  best_M = M[indices]                              # .... and get best_M at same 'index' and ....
  best_F = np.take_along_axis(F, indices, axis=1)  # .... get best_F at same 'index'
  return best_F<<20 | best_M<<8 | N


def pt_MHz_to_fmn(target_freqs: torch.Tensor, M: torch.Tensor, Fpfd: torch.float16=66.0, device='cpu'):
  """ Form a 32 bit word consisting of 12 bits of F, 12 bits of M and 8 bits of N for the MAX2871. """
  div = 2**torch.arange(8).to(device)
  target_freqs = target_freqs.cuda().to(device)
  Fvco = (div * target_freqs.view(-1, 1))
  target_freqs = target_freqs.to(device)
  div_mask = (Fvco >= 3000).to(dtype=torch.int)
  indices = torch.argmax(div_mask, dim=1).view(-1, 1)   # Using indices for Fvco masking
  Fvco = Fvco.gather(1, indices)
  """ Fpfd is the step bandwidth. Dividing Fvco by Fpfd gives the total number
      of steps with a small fraction. The result is split into an integer, N, 
      and a decimal fraction, F, for programming the MAX2871 registers.
  """
  N = (Fvco/Fpfd).to(torch.int16)  # Integer portion of the step size for register N
  step_fract = (Fvco/Fpfd - N)    # Decimal portion of the step size
  """ F must be 64 bit to prevent overflow when left-shifting 20 bits at *return* """
  F = (M * step_fract).to(torch.int64)  # Convert decimal part for register F
#  indices = torch.argmin((torch.abs(Fvco - (Fpfd * (N + F/M)))), dim=1).view(-1, 1)   # Reuse indices for Min-Error
  Fvco_diffs = torch.abs(Fvco - (Fpfd * (N + F/M)))
  indices = torch.argmin(Fvco_diffs, dim=1).view(-1, 1)   # Reuse indices for Min-Error
  best_M = M[indices]
  best_F = F.gather(1, indices)         # indices is the index that results in best_F
  return best_F<<20 | best_M<<8 | N


def collect_M_ties(
    frange,
    device=None,
    batch_size=16_384,
    max_examples=None,
    ties_only=True,
):
    """
    For each frequency in the sweep, find all M values (2..4095) whose error
    matches the minimum error for that frequency, after rounding error to kHz.

    Frequencies are stored and keyed as MHz rounded to 3 decimals.
    """
    import numpy as np
    import torch

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device)

    sweep_freqs, step_size = build_sweep(frange)

    target_freqs = torch.from_numpy(sweep_freqs.astype(np.float32)).to(device)

    M = torch.arange(2, 4096, dtype=torch.int32, device=device)      # [nM]
    Fpfd_t = torch.tensor(Fpfd, dtype=torch.float32, device=device)  # scalar
    div = 2 ** torch.arange(8, device=device)                        # [8]

    freq_M_targets = {}
    saved = 0

    start_t = perf_counter()

    for batch_freqs in target_freqs.split(batch_size):
        B = batch_freqs.shape[0]

        # 1) VCO ladder and first multiplier with Fvco >= 3000
        Fvco_ladder = batch_freqs.view(-1, 1) * div.view(1, -1)      # [B, 8]
        div_mask = (Fvco_ladder >= 3000.0).to(torch.int)
        idx = torch.argmax(div_mask, dim=1)                          # [B]
        Fvco = Fvco_ladder[torch.arange(B, device=device), idx]      # [B]

        # 2) N and fractional part
        step_total = Fvco / Fpfd_t                                   # [B]
        N = step_total.to(torch.int16)                               # [B]
        step_fract = step_total - N                                  # [B]

        # 3) All F candidates for all M
        F = (step_fract.view(-1, 1) * M.view(1, -1)).to(torch.int64) # [B, nM]

        # 4) Error surface in MHz
        F_over_M = F.to(torch.float32) / M.view(1, -1)               # [B, nM]
        synth = Fpfd_t * (N.view(-1, 1).to(torch.float32) + F_over_M)
        diffs = torch.abs(Fvco.view(-1, 1) - synth)                  # [B, nM]

        # Quantize error to integer kHz and use strict equality
        diffs_kHz = torch.round(diffs * 1000.0)                      # [B, nM]
        row_min_kHz, _ = diffs_kHz.min(dim=1)                        # [B]
        tie_mask = diffs_kHz == row_min_kHz.view(-1, 1)              # [B, nM]

        # Canonical best_M from quantized error
        idx_min = torch.argmin(diffs_kHz, dim=1)                     # [B]
        best_M = M[idx_min]                                          # [B]

        # Move small things to CPU for dict population
        freqs_cpu        = batch_freqs.cpu().numpy()
        row_min_kHz_cpu  = row_min_kHz.cpu().numpy()
        best_M_cpu       = best_M.cpu().numpy()
        tie_mask_cpu     = tie_mask.cpu().numpy()
        M_cpu            = M.cpu().numpy()

        for i in range(B):
            Ms_tied = M_cpu[tie_mask_cpu[i]].astype(int).tolist()

            if ties_only and len(Ms_tied) <= 1:
                continue

            # Raw float from GPU
            freq_MHz = float(freqs_cpu[i])
            # Round to 3 decimals (1 kHz resolution)
            freq_MHz_rounded = round(freq_MHz, 3)

            best_err_kHz = float(row_min_kHz_cpu[i])
            best_M_val   = int(best_M_cpu[i])

            freq_M_targets[freq_MHz_rounded] = {
                "freq_MHz":  freq_MHz_rounded,
                "error_kHz": best_err_kHz,
                "best_M":    best_M_val,
                "M_list":    Ms_tied,
            }

            saved += 1
            if max_examples is not None and saved >= max_examples:
                break

        if max_examples is not None and saved >= max_examples:
            break

    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elapsed = perf_counter() - start_t

    print(
        line(),
        f"collect_M_ties() captured {saved} frequencies "
        f"in {elapsed:.3f} s on {device}",
    )
    return freq_M_targets

        """
        # 4) Error surface for all (F,M)
        F_over_M = F.to(torch.float32) / M.view(1, -1)               # [B, nM]
        synth = Fpfd_t * (N.view(-1, 1).to(torch.float32) + F_over_M)  # [B, nM]
        diffs = torch.abs(Fvco.view(-1, 1) - synth)                  # [B, nM]

        # 5) Minimum error per row, and tie mask
        row_min, _ = diffs.min(dim=1)                                # [B]
        tie_mask = torch.isclose(
            diffs,
            row_min.view(-1, 1),
            rtol=rtol,
            atol=atol,
        )                                                            # [B, nM]

        # 6) Canonical best_M = first argmin (keeps current behaviour)
        idx_min = torch.argmin(diffs, dim=1)                         # [B]
        best_M = M[idx_min]                                          # [B]
        """

        # Move small things to CPU for dict construction
        freqs_cpu    = batch_freqs.cpu().numpy()
        row_min_kHz_cpu = row_min_kHz.cpu().numpy()
        best_M_cpu   = best_M.cpu().numpy()
        tie_mask_cpu = tie_mask.cpu().numpy()
        M_cpu        = M.cpu().numpy()
        """
        freqs_cpu     = batch_freqs.cpu().numpy()
        row_min_cpu   = row_min.cpu().numpy()
        best_M_cpu    = best_M.cpu().numpy()
        tie_mask_cpu  = tie_mask.cpu().numpy()
        M_cpu         = M.cpu().numpy()
        """

        for i in range(B):
            freq_MHz = float(freqs_cpu[i])

            # Already in kHz, rounded to integer
            best_err_kHz = float(row_min_kHz_cpu[i])

            Ms_tied = M_cpu[tie_mask_cpu[i]].astype(int).tolist()

            freq_M_targets[freq_MHz] = {
                "error_kHz": best_err_kHz,
                "best_M":    int(best_M_cpu[i]),
                "M_list":    Ms_tied,
            }
            """
            # Which M values tie for the minimum?
            Ms_tied = M_cpu[tie_mask_cpu[i]].astype(int).tolist()

            if ties_only and len(Ms_tied) <= 1:
                continue  # skip single-M minima if you only care about ties

            freq_MHz = float(freqs_cpu[i])
            best_err_kHz = float(row_min_cpu[i]) * 1000.0
            best_M_val = int(best_M_cpu[i])

            freq_M_targets[freq_MHz] = {
                "error_kHz": best_err_kHz,
                "best_M":    best_M_val,
                "M_list":    Ms_tied,
            }
            """

            saved += 1
            if max_examples is not None and saved >= max_examples:
                break

        if max_examples is not None and saved >= max_examples:
            break

    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elapsed = perf_counter() - start_t

    print(
        line(),
        f"collect_M_ties() captured {saved} frequencies "
        f"in {elapsed:.3f} s on {device}",
    )
    return freq_M_targets


def summarize_M_ties(freq_M_targets):
    """
    Given freq_M_targets from collect_M_ties(), find:
      - the frequency with the fewest tied M values
      - the frequency with the most tied M values

    Returns:
        (min_freq, min_count), (max_freq, max_count)
    """
    min_freq = None
    min_count = None
    max_freq = None
    max_count = None

    for freq, info in freq_M_targets.items():
        count = len(info["M_list"])

        if min_count is None or count < min_count:
            min_count = count
            min_freq = freq

        if max_count is None or count > max_count:
            max_count = count
            max_freq = freq

    print(line(), f"fewest M's: freq = {min_freq:.3f} MHz, count = {min_count}")
    print(line(), f"most   M's: freq = {max_freq:.3f} MHz, count = {max_count}")

    return (min_freq, min_count), (max_freq, max_count)


def report_cuda_memory(device='cuda:0'):
    total_memory = torch.cuda.get_device_properties(device).total_memory
    allocated_memory = torch.cuda.memory_allocated(device)
    cached_memory = torch.cuda.memory_cached(device)

    print(f"Device: {device}")
    print(f"Total GPU Memory: {total_memory}")
    print(f"Allocated Memory: {allocated_memory}")
    print(f"Cached Memory: {cached_memory}")
"""
    total_memory = torch.cuda.get_device_properties(device).total_memory / (1024**2)  # Convert bytes to MB
    allocated_memory = torch.cuda.memory_allocated(device) / (1024**2)  # Convert bytes to MB
    cached_memory = torch.cuda.memory_cached(device) / (1024**2)  # Convert bytes to MB

    print(f"Total GPU Memory: {total_memory:.2f} MB")
    print(f"Allocated Memory: {allocated_memory:.2f} MB")
    print(f"Cached Memory: {cached_memory:.2f} MB")
"""


def build_sweep(frange):
    """Return (sweep_freqs, step_size) for a given (start, end, num_steps)."""
    start, end, num_steps = frange
    print(line(), f'start = {start}, end = {end}, steps = {num_steps}')
    step_size = (end - start) / num_steps

    # If you want to mimic your old “end + step/10” trick, do it here:
    end_adjusted = end + step_size / 10.0
    sweep_freqs = np.arange(start, end_adjusted, step_size)
    sweep_freqs = np.round(sweep_freqs, 3)

    return sweep_freqs, step_size


def num_py(frange):
    sweep_freqs, step_size = build_sweep(frange)

    scalar_freqs = []
    scalar_fmn   = []
    scalar_fvco  = []

    start_a = perf_counter()
    for freq in sweep_freqs:
        fmn, fvco = MHz_to_fmn(float(freq), ref_clock)
        # print(line(), f'fmn = {hex(fmn)} : fvco = {round(fvco, 3)}')
        scalar_freqs.append(freq)
        scalar_fmn.append(fmn)
        scalar_fvco.append(fvco)

    elapsed = perf_counter() - start_a
    print(line(), f'num_py() processed {len(scalar_freqs)} points in {elapsed:.3f} s')

    return (
        np.array(scalar_freqs),
        np.array(scalar_fmn, dtype=np.uint32),
        np.array(scalar_fvco, dtype=np.float64),
    )


def py_torch(frange, device=None, batch_size=16_384):
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(device)

    sweep_freqs, step_size = build_sweep(frange)

    # Convert sweep to Torch on the selected device
    target_freqs = torch.from_numpy(sweep_freqs.astype(np.float32)).to(device)

    # Precompute M and Fpfd on device
    M = torch.arange(2, 4096, dtype=torch.int32, device=device)
    Fpfd_t = torch.tensor(Fpfd, dtype=torch.float32, device=device)

    # Run in batches to control memory use
    fmns_torch = []
    start_b = perf_counter()
    for batch in target_freqs.split(batch_size):
        batch_fmn = pt_MHz_to_fmn(batch, M, Fpfd=Fpfd_t, device=device)
        fmns_torch.append(batch_fmn)

    fmns_torch = torch.cat(fmns_torch)
    elapsed = perf_counter() - start_b
    print(line(), f'py_torch() processed {len(sweep_freqs)} points in {elapsed:.3f} s on {device}')

    return sweep_freqs, fmns_torch.cpu().numpy()


""" # Old py_torch()
def py_torch(frange):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dev_capability = torch.cuda.get_device_capability()
    print(line(), f'GPU Capability : {dev_capability}')
    print(line(), f'{device = }\n')

    start, end, num_steps = frange
    step_size = (end - start)/num_steps

    scalar_fmn = []
    scalar_fvcos = []
    scalar_freqs = []
    torch_fmn = []
  #  batch_size = 65_000
    batch_size = 16350    # This batch size causes 1.0 GB of video ram to be consumed
    sweep_freqs, step_size = build_sweep(frange)

    dataloader = DataLoader(sweep_freqs, batch_size=batch_size, shuffle=False, num_workers=cpus)
    start_a = perf_counter()
    n = 13

    ''' Run the Pytorch version of MHz_to_fmn() '''
    M = (torch.arange(2, 4096)).to(torch.int32)
    M = M.to(device)
    start_b = perf_counter()
    num_batches = 0
    sum_points = 0
    for batch in dataloader:
      num_batches += 1
      sum_points += len(torch_fmn)
      batch = np.round(batch, decimals=3)
      torch_fmn = pt_MHz_to_fmn(batch, M, device=device).cpu().numpy()
    if num_batches == 1:
      pt_str = f'{num_batches} batch'
    else:
      pt_str = f'{num_batches} batches'
    elapsed = perf_counter() - start_b
    print(line(), f'num_py() processed {sum_points} points in {elapsed:.3f} s')
"""


def main():
  print()
  frange = (23.5, 6000.0, 5_976_000)

  freq_M_targets = collect_M_ties(
    frange,
    device="cuda",
    batch_size=16_384,
    max_examples=1000,   # or None if you really want all of them
    ties_only=True,      # only keep frequencies with >1 M in M_list
  )

  for f, info in list(freq_M_targets.items())[:5]:
    print(
      f"{f:.3f} MHz -> err={info['error_kHz']:.6f} kHz, "
      f"best_M={info['best_M']}, M_list={info['M_list']}"
    )

  (min_freq, min_count), (max_freq, max_count) = summarize_M_ties(freq_M_targets)

  # num_py(frange)
  # print()
  # py_torch(frange)
  print()

if __name__ == '__main__':
  cpus = int(cpu_count() / 2)
  print(line(), f'number of CPUs = {cpus}')

  main()















