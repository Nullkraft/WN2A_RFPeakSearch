import torch
from torch.utils.data import DataLoader, Dataset
import numpy as np
import sys

line = lambda: f"line {str(sys._getframe(1).f_lineno)},"

np.set_printoptions(precision=8)
# torch.set_printoptions(sci_mode=False)
torch.set_printoptions(threshold=float('inf'))
R = 2
ref_clock = 66.0
Fpfd = ref_clock / R
div_range = torch.arange(8)
div = 2**div_range
div = div.cuda()
M_range = range(2, 4096)


def fmn_to_MHz(fmn_word, Fpfd: float=33.0, show_fmn: bool=False):
  F_ = fmn_word >> 20
  M_= (fmn_word & 0xFFFFF) >> 8
  if M_ == 0:
      M_ = 2
  N_ = fmn_word & 0xFF
  if show_fmn:
      print('\t', f'M:F:N = {M_.item(),F_.item(),N_.item()}')
  freq_MHz = Fpfd * (N_ + F_/M_)
  return freq_MHz

def MHz_to_fmn(target_freqs: torch.Tensor, M: torch.Tensor, Fpfd: torch.float16=33.0):
  """ Form a 32 bit word consisting of 12 bits of F, 12 bits of M and 8 bits of N for the MAX2871. """
#  target_freqs = target_freqs.to(torch.float64).view(-1, 1)
#  Fvco_targs = (div * target_freqs)
  Fvco_targs = (div * target_freqs.view(-1, 1))
  div_mask = (Fvco_targs >= 3000).to(torch.int)
  indices = torch.argmax(div_mask, dim=1).view(-1, 1)
  target_Fvcos = Fvco_targs.gather(1, indices)
#  target_Fvcos = torch.round(Fvco_targs.gather(1, indices), decimals=3)
  """ Fpfd is the bandwidth of a step and dividing Fvco by Fpfd gives our total number of steps
  plus a small fraction. This needs to be separated into the integer and decimal parts for
  programming the MAX2871 registers, N and F, respectively.
  """
  N = (target_Fvcos/Fpfd).to(torch.int8)  # Integer portion of the step size for register N
  step_fract = (target_Fvcos/Fpfd - N)    # Decimal portion of the step size
  """ F must be 64 bit to prevent overflow when left-shifting 20 bits at *return* """

  print(line(), f'1) Peak mem = {torch.cuda.max_memory_allocated()/10**6} MB')

  F = (M * step_fract).to(torch.int64)    # Convert decimal part for register F
#  F = (M * step_fract).to(torch.int64)    # Convert decimal part for register F

#  print(line(), f'1) Peak mem = {torch.cuda.max_memory_allocated()/10**9} GB')

#  actual_Fvcos = Fpfd * (N + F/M).to(torch.float64)

  print(line(), f'1) Peak mem = {torch.cuda.max_memory_allocated()/10**9} GB')

  Fvco_differences = torch.abs(target_Fvcos - (Fpfd * (N + F/M).to(torch.float64)))
#  Fvco_differences = torch.abs(target_Fvcos - actual_Fvcos)

  print(line(), f'1) Peak mem = {torch.cuda.max_memory_allocated()/10**9} GB')

  indices = torch.argmin(Fvco_differences, dim=1).view(-1, 1) # Overwrite previous indices
  best_M = M[indices]
  best_F = F.gather(1, indices)           # indices is the index that results in best_F
  return best_F<<20 | best_M<<8 | N

class FrequencyDataset(Dataset):
  def __init__(self, frequencies):
    self.frequencies = frequencies
  
  def __len__(self):
    return len(self.frequencies)
  
  def __getitem__(self, idx):
    return self.frequencies[idx]


if __name__ == '__main__':
  from time import perf_counter
  torch.set_printoptions(sci_mode=False)
  print()

  M = (torch.arange(2, 4096)).to(torch.int32).cuda()

  num_steps = 66_000
  num_steps_disp = 66_000
  start = 4082.0
  end = 4148.0
  step_size = (end - start)/num_steps
  end = end + step_size/10
  steps = np.round(np.arange(start, end, step_size), decimals=3)

  ret_gpu = []
  target_freqs_gpu = torch.arange(start, end, step_size).cuda()
  dataset = FrequencyDataset(target_freqs_gpu)
  chunk_size = 2000
  dataloader = DataLoader(target_freqs_gpu, batch_size=chunk_size)
#  start = perf_counter()

#  for chunk in dataloader:
#    ret_gpu = MHz_to_fmn(chunk, M).cpu().numpy()
#  ret_gpu = [MHz_to_fmn(chunk, M).cpu().numpy() for chunk in dataloader]
  ret_gpu = MHz_to_fmn(target_freqs_gpu, M).cpu().numpy()
#  print(line(), f'Interval = {round(perf_counter()-start, 6)} seconds\n')
  print()

  freqs = [fmn_to_MHz(fmn) for fmn in ret_gpu]
  freqs = np.round(np.array(freqs), decimals=3)
  n = len(freqs)
  freqs = freqs.flatten()
  for i in range(n):
    if not np.array_equal(steps[i], freqs[i]):
      delta = round(abs((steps[i]-freqs[i])), 3)
      if delta > 0.007:
#        print(line(), f'FREQUENCY ERROR AT INDEX [{i}]')
#        print(line(), f'steps[{i}] = {steps[i]}\tfmn_to_MHz[{i}] = {freqs[i]}')
        print(line(), f'delta [{i}] = {delta}')















