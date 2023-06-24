import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import sys

line = lambda: f"line {str(sys._getframe(1).f_lineno)},"

R = 2
ref_clock = 66.0
Fpfd = ref_clock / R

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

def MHz_to_fmn(target_freqs: torch.Tensor, M: torch.Tensor, Fpfd: torch.float16=33.0, device='cpu'):
  """ Form a 32 bit word consisting of 12 bits of F, 12 bits of M and 8 bits of N for the MAX2871. """
  div = 2**torch.arange(8).to(device)
  target_freqs = target_freqs.cuda().to(device)
  M = M.cuda().to(device)
  Fvco_targs = (div * target_freqs.view(-1, 1))
  div_mask = (Fvco_targs >= 3000).to(torch.int)
  indices = torch.argmax(div_mask, dim=1).view(-1, 1)   # Using indices for Fvco mask >3000
  Fvco_targs = Fvco_targs.gather(1, indices)
  """ Fpfd is the step bandwidth and dividing Fvco by Fpfd gives the total number of steps
  with a small fraction. This will need to be separated into an integer and a decimal for
  programming the MAX2871 registers, N and F, respectively.
  """
  N = (Fvco_targs/Fpfd).to(torch.int8)  # Integer portion of the step size for register N
  step_fract = (Fvco_targs/Fpfd - N)    # Decimal portion of the step size
  """ F must be 64 bit to prevent overflow when left-shifting 20 bits at *return* """
  F = (M * step_fract).to(torch.int64)  # Convert decimal part for register F
  Fvco_differences = torch.abs(Fvco_targs - (Fpfd * (N + F/M)))
  indices = torch.argmin(Fvco_differences, dim=1).view(-1, 1)   # Reuse indices for Least Error
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
  print()

  M = (torch.arange(2, 4096)).to(torch.int32)
  start = 0.0
  end = 3000.0
  num_steps = 10
  num_steps = (end-start) / 0.001
#  start = 4082.0
#  end = 4148.0
  step_size = (end - start)/num_steps
  end = end + step_size/10
  steps = np.round(np.arange(start, end, step_size), decimals=3)
  print(line(), f'steps =\n{steps}')

  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  M = M.to(device)

  all_fmn = []
  batch_size = 16350    # This batch size causes 1.0 GB of video ram to be consumed
  sweep_freqs = FreqDataset(start, end, step_size)
  dataloader = DataLoader(sweep_freqs, batch_size=batch_size, shuffle=False, num_workers=0)
  start_a = perf_counter()
  for batch in dataloader:
      target_freqs = batch.to(device)
      fmn_batch = MHz_to_fmn(target_freqs, M, device=device).cpu().numpy()
      all_fmn.append(fmn_batch)
  print(line(), f'All batches took {round(perf_counter()-start_a, 6)} seconds')
  ret_gpu = np.concatenate(all_fmn)   # all_fmn is a list of lists so cat them all together
  print(line(), f'Max cuda memory = {round(torch.cuda.max_memory_allocated()/1024**3, 3)} GB')
  
  Fvcos = [fmn_to_MHz(fmn, Fpfd, show_fmn=False) for fmn in ret_gpu]  # Verify results by converting back to frequency
  Fvcos = np.round(np.array(Fvcos), decimals=3).flatten()

  deltas = []
  for i, freq in enumerate(Fvcos):
    Fvco = freq
    while True:
      if Fvco <= steps[i]:# + 0.0006:
        break
      Fvco = Fvco/2
    if not np.array_equal(steps[i], Fvco):
      delta = abs((steps[i]-Fvco))
      if delta > 0.008:
#        print(line(), f'Frequency step {i} = {steps[i]}\t\tfmn_to_MHz[{i}] = {Fvcos[i]}\t\t{delta = }')
        deltas.append(delta)
#      count += 1
  
  print(line(), f'Max delta = {max(deltas)}')
#  print(line(), f'Num errors < = {max(lwr)}')





