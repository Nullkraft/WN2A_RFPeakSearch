import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import sys
from hardware_cfg import MHz_to_fmn

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
  global F_list
  global diffs
  """ Form a 32 bit word consisting of 12 bits of F, 12 bits of M and 8 bits of N for the MAX2871. """
  div = 2**np.arange(8)                           # Create 8 Fpfd multipliers ...
  Fvco = div * target_freqs[:, None]              # ... to reach Fvco = (vco => 3000 MHz)
  div_mask = Fvco >= 3000                         # table of True/False: Which of the 8 are >3000?
  indices = np.argmax(div_mask, axis=1)[:, None]  # Using indices for Fvco masking
  Fvco = np.take_along_axis(Fvco, indices, axis=1)# Done with indicies, now it can be used elsewhere
  N = (Fvco/Fpfd).astype(np.int16)                # Integer portion of the step size for register N
  step_fract = Fvco/Fpfd - N                      # Decimal portion of the step size
  F = (M * step_fract).astype(np.int64)           # Convert decimal part for register F
  Fvco_diffs = np.abs(Fvco - (Fpfd * (N + F/M)))
  indices = np.argmin(Fvco_diffs, axis=1)[:, None] # Get the index of the minimum error ....
  best_M = M[indices]                              # .... and get best_M at same 'index' and ....
  best_F = np.take_along_axis(F, indices, axis=1)  # .... get best_F at same 'index'
  return best_F<<20 | best_M<<8 | N

pr = True
def pt_MHz_to_fmn(target_freqs: torch.Tensor, M: torch.Tensor, Fpfd: torch.float16=33.0, device='cpu'):
  global pr
  """ Form a 32 bit word consisting of 12 bits of F, 12 bits of M and 8 bits of N for the MAX2871. """
  div = 2**torch.arange(8).to(device)
#  target_freqs = target_freqs.cuda().to(device)
  Fvco = (div * target_freqs.view(-1, 1))
  target_freqs = target_freqs.to(device)
  div_mask = (Fvco >= 3000).to(dtype=torch.int)
  indices = torch.argmax(div_mask, dim=1).view(-1, 1)   # Using indices for Fvco masking
  Fvco = Fvco.gather(1, indices)
  if pr == True:
    pr = False
#    print(line(), f'{target_freqs[0] = }, Fvco = {Fvco[0]}')
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

class FreqDataset(Dataset):
    def __init__(self, start, end, step_size):
        self.freqs = torch.arange(start, end, step_size)

    def __len__(self):
        return len(self.freqs)

    def __getitem__(self, idx):
        return self.freqs[idx]

def report_cuda_memory(device='cuda:0'):
    total_memory = torch.cuda.get_device_properties(device).total_memory
    allocated_memory = torch.cuda.memory_allocated(device)
    cached_memory = torch.cuda.memory_cached(device)

    print(f"Device: {device}")
    print(f"Total GPU Memory: {total_memory}")
    print(f"Allocated Memory: {allocated_memory}")
    print(f"Cached Memory: {cached_memory}")
"""
#    total_memory = torch.cuda.get_device_properties(device).total_memory / (1024**2)  # Convert bytes to MB
#    allocated_memory = torch.cuda.memory_allocated(device) / (1024**2)  # Convert bytes to MB
#    cached_memory = torch.cuda.memory_cached(device) / (1024**2)  # Convert bytes to MB
#
#    print(f"Total GPU Memory: {total_memory:.2f} MB")
#    print(f"Allocated Memory: {allocated_memory:.2f} MB")
#    print(f"Cached Memory: {cached_memory:.2f} MB")
"""

if __name__ == '__main__':
  print()
  from time import perf_counter
  from os import cpu_count
#  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#  dev_capability = torch.cuda.get_device_capability()
#  print(line(), f'GPU Capability : {dev_capability}')
  device = torch.device('cpu')
#  print(line(), f'{device = }\n')

  start = 3352.015
  end = 3355.015
  num_steps = 3
#  num_steps = round((end-start) / 0.001)
  print(line(), f'start = {start}, end = {end}, steps = {num_steps}')
#  start = 4082.0
#  end = 4148.0
  step_size = (end - start)/num_steps
  end = end + step_size/10      # Add a small fraction of a step to include the 'end' value
  steps = np.arange(start, end, step_size)
#  print(line(), f'steps =\n{steps}')

  norm_fmn = []
  norm_fvcos = []
  norm_freqs = []
  torch_fmn = []
#  batch_size = 65_000
  batch_size = 16350    # This batch size causes 1.0 GB of video ram to be consumed
  sweep_freqs = np.round(FreqDataset(start, end, step_size), 3)
  
  cpus = int(cpu_count() / 2)
  print(line(), f'number of CPUs = {cpus}')
  dataloader = DataLoader(sweep_freqs, batch_size=batch_size, shuffle=False, num_workers=cpus)
  print(line(), f'{len(sweep_freqs) = }, {dataloader.dataset}')
  start_a = perf_counter()
  for freq in sweep_freqs:
    fmn, norm_fvco = MHz_to_fmn(freq, 33.0)
    print(line(), f'fmn = {hex(fmn)} : norm_fvco = {round(norm_fvco, 3)}')
    norm_freqs.append(freq)
    norm_fmn.append(fmn)
    norm_fvcos.append(norm_fvco)
#  n = 13
#  print(line(), f'norm fmn[{n}] = {norm_fmn[n]}')

  """ Run the Pytorch version of MHz_to_fmn() """  
  M = (torch.arange(2, 4096)).to(torch.int32)
  M = M.to(device)
  start_b = perf_counter()
  num_batches = 0
  for batch in dataloader:
    num_batches += 1
    batch = np.round(batch, decimals=3)
    torch_fmn = pt_MHz_to_fmn(batch, M, device=device).cpu().numpy()
  if num_batches == 1:
    pt_str = f'{num_batches} batch'
  else:
    pt_str = f'{num_batches} batches'

#  print(line(), f'"PyTorch" ran {pt_str} and took {round((perf_counter()-start_b), 4)} sec on the "{str(device)}"')
#  print(line(), report_cuda_memory())
  diffs = []
  for i, fmn in enumerate(torch_fmn):
    Tfmn = fmn_to_MHz(fmn[0],Fpfd)
    Nfmn = fmn_to_MHz(norm_fmn[i], Fpfd)
    NFvco = norm_fvcos[i]
    NFreq = norm_freqs[i]
    delta = round(Nfmn-Tfmn, 3)
    if abs(delta) > 0.0:
      diffs.append([NFreq, round(Nfmn,3), round(Tfmn,3), delta])
#  print(line(), f'norm Fvco = {[round(f,3) for f in norm_fvcos[235:244]]}')
  print(line(), f'{len(norm_fvcos)}')
  print(line(), f'{len(diffs) = }')
  print(line())
  print(diffs)
#  dees = []
#  for d in diffs:
#    if d[3] >.008:
#      dees.append(d[0])
#  print(dees)






  """
  np_M = np.arange(2, 4096)
  np_all_fmn = []
  np_num_batches = 0
  start_a = perf_counter()
  if 1:
    for batch in dataloader:
      # Convert PyTorch tensor to numpy array
      np_num_batches += 1
      target_freqs = batch.numpy()
      print(line(), f'Batch from {np.round(target_freqs[0], decimals=3)} to {round(target_freqs[-1], 3)} MHz')
      fmn_batch = np_MHz_to_fmn(target_freqs, np_M)
      np_all_fmn.append(fmn_batch)
    if np_num_batches == 1:
      np_str = f'{np_num_batches} batch'
    else:
      np_str = f'{np_num_batches} batches'

  print(line(), f'"Numpy"   ran {np_str} and took {round(perf_counter()-start_a, 6)} sec on the "cpu"')
  print(line(), f'Size of FMNs = {len(np_all_fmn)}')
  """


















