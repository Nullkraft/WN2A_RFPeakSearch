import torch
# ~ from torch.utils.data import Dataset, DataLoader
import numpy as np
import sys
from time import perf_counter
from os import cpu_count

line = lambda: f"line {str(sys._getframe(1).f_lineno)},"    # Report which line in the file

R = 1
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

  py_torch(frange, 'cuda')    # Approx 2 seconds to completion
#  print()
#  py_torch(frange, 'cpu')    # Approx 108 seconds to completion

  print()

if __name__ == '__main__':
  cpus = int(cpu_count() / 2)
  print(line(), f'number of CPUs = {cpus}')

  main()















