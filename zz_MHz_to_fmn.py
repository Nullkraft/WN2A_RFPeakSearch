import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import sys

line = lambda: f"line {str(sys._getframe(1).f_lineno)},"

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

R = 2
ref_clock = 66.666
Fpfd = ref_clock / R
def np_MHz_to_fmn(target_freqs: np.ndarray, M: np.ndarray, Fpfd: float =33.0):
  """ Form a 32 bit word consisting of 12 bits of F, 12 bits of M and 8 bits of N for the MAX2871. """
  div = 2**np.arange(8)
  Fvco = div * target_freqs[:, None]
  div_mask = Fvco >= 3000
  indices = np.argmax(div_mask, axis=1)[:, None]   # Using indices for Fvco masking
  Fvco = np.take_along_axis(Fvco, indices, axis=1)
  N = (Fvco/Fpfd).astype(np.int16)  # Integer portion of the step size for register N
  step_fract = Fvco/Fpfd - N    # Decimal portion of the step size
  F = (M * step_fract).astype(np.int64)  # Convert decimal part for register F
  Fvco_diffs = np.abs(Fvco - (Fpfd * (N + F/M)))
  indices = np.argmin(Fvco_diffs, axis=1)[:, None]   # Reuse indices for Min-Error
  best_M = M[indices]
  best_F = np.take_along_axis(F, indices, axis=1)  # indices is the index that results in best_F
  return best_F<<20 | best_M<<8 | N

def MHz_to_fmn(target_freqs: torch.Tensor, M: torch.Tensor, Fpfd: torch.float16=33.0, device='cpu'):
  """ Form a 32 bit word consisting of 12 bits of F, 12 bits of M and 8 bits of N for the MAX2871. """
  div = 2**torch.arange(8).to(device)
  target_freqs = target_freqs.cuda().to(device)
  M = M.cuda().to(device)
  Fvco = (div * target_freqs.view(-1, 1))
  div_mask = (Fvco >= 3000).to(torch.int)
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
  Fvco_diffs = torch.abs(Fvco - (Fpfd * (N + F/M)))
  indices = torch.argmin(Fvco_diffs, dim=1).view(-1, 1)   # Reuse indices for Min-Error
  best_M = M[indices]
  best_F = F.gather(1, indices)         # indices is the index that results in best_F
  return best_F<<20 | best_M<<8 | N

class FreqDataset(Dataset):
    def __init__(self, start, end, step_size):
        self.freqs = torch.arange(start, end, step_size)

    def __len__(self):
        return len(self.freqs)

    def __getitem__(self, idx):
        return self.freqs[idx]

if __name__ == '__main__':
  from time import perf_counter
  from os import cpu_count
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#  device = torch.device('cpu')
  print(line(), f'{device = }')

  start = 23.5
  end = 6000.0
  num_steps = 1201
#  num_steps = (end-start) / 0.001
#  start = 4082.0
#  end = 4148.0
  step_size = (end - start)/num_steps
  end = end + step_size/10      # Add a small fraction of a step to include the 'end' value
  steps = np.round(np.arange(start, end, step_size), decimals=3)
#  print(line(), f'steps =\n{steps}')

  all_fmn = []
  batch_size = 65_000
#  batch_size = 16350    # This batch size causes 1.0 GB of video ram to be consumed
  sweep_freqs = FreqDataset(start, end, step_size)
  cpus = int(cpu_count() / 2)
  dataloader = DataLoader(sweep_freqs, batch_size=batch_size, shuffle=False, num_workers=cpus)

  num_batches = 0



  np_M = np.arange(2, 4096)
  np_all_fmn = []
  start_a = perf_counter()
  for batch in dataloader:
    # Convert PyTorch tensor to numpy array
    num_batches += 1
    target_freqs = batch.numpy()
    fmn_batch = np_MHz_to_fmn(target_freqs, np_M)
    np_all_fmn.append(fmn_batch)
  stop_a = perf_counter()

  M = (torch.arange(2, 4096)).to(torch.int32)
  M = M.to(device)
  start_b = perf_counter()
  " WARNING: Limit num_steps to 1600 or less. "
  " Wait for a bigger battery backup. This code draws too much power! "
  for batch in dataloader:
    num_batches += 1
    target_freqs = batch.to(device)
    fmn_batch = MHz_to_fmn(target_freqs, M, device=device).cpu().numpy()
    all_fmn.append(fmn_batch)




  print(line(), f'{num_batches} batches on "Numpy" using the "CPU" took {round(stop_a-start_a, 4)} seconds')
  print(line(), f'{num_batches} batches on "PyTorch" using the "{str(device).upper()}" took {round(perf_counter()-start_b, 4)} seconds')
#  ret_gpu = np.concatenate(all_fmn)   # all_fmn is a list of lists so cat them all together
#  print(line(), f'Max cuda memory = {round(torch.cuda.max_memory_allocated()/1024**3, 3)} GB')
  print(line(), f'Max cuda memory = {round(torch.cuda.max_memory_allocated()/1024**3, 3)} GB')
  
#  print(line(), f'{type(ret_gpu) = } // {ret_gpu.shape = } :// {np.max(ret_gpu) = }')

##  # Verify results by converting back to frequency
##  Fvcos = [fmn_to_MHz(fmn, Fpfd, show_fmn=False) for fmn in ret_gpu]
##  Fvcos = np.round(np.array(Fvcos), decimals=3).flatten()
##  deltas = []
##  freqs = []
##  for i, Fvco in enumerate(Fvcos):
##    while True:
##      if Fvco <= steps[i]:# + 0.0006:   # Fix the Fvco that does one too many divides
##        break
##      Fvco = Fvco/2
##    if not np.array_equal(steps[i], Fvco):
##      delta = round(abs((steps[i]-Fvco)), 3)
##      if delta > 0.001:
##        deltas.append(delta)
##        freqs.append(Fvco)
##
##  print(line(), f'Num items > 1 kHz error = {len(deltas)} vs. {len(Fvcos) = }')
##  if len(deltas) > 0:
##    for i, _ in enumerate(deltas[:100]):
##      pass
###      print(line(), f'{deltas[i]}:{freqs[i]}')
##    print(line(), f'{i = }')





