import torch
import sys
from math import log
from time import perf_counter
from os import cpu_count

line = lambda: f"line {str(sys._getframe(1).f_lineno)},"    # Report which line in the file

R = 1
ref_clock = 66.000
Fpfd = ref_clock / R


def freq2fmn(target_freqs: torch.Tensor, M: torch.Tensor, Fpfd: torch.float32=66.0, device='cpu'):
  """ Form a 32 bit word consisting of 12 bits of F, 12 bits of M and 8 bits of N for the MAX2871. """
  div = 2**torch.arange(8).to(device)
  target_freqs = target_freqs.cuda().to(device)
#  print(line(), f'target_freqs = {target_freqs[0]} to {target_freqs[-1]}')

  Fvco = (div * target_freqs.view(-1, 1))
  target_freqs = target_freqs.to(device)
  div_mask = (Fvco >= 3000).to(dtype=torch.int)
  indices = torch.argmax(div_mask, dim=1).view(-1, 1)   # finds first divider that keeps Fvco in the VCO range
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
  return best_F<<20 | best_M<<8 | N     # Assemble best_F, best_M, and N into a 32bit FMN return value




def calculate_gpu_batch_size(device):
    """
    Calculate batch size based on available VRAM, rounded down to nearest power of 2.
    Results based on empirical measurement: ~62 KB per batch item

    Rounding to powers of 2 serves two purposes:
        Prevents memory overflow: batch sizes are internally allocated in powers of 2,
    """
    if device == 'cpu' or device == None:
        return 16_384  # fallback for CPU

    free_memory_bytes, _ = torch.cuda.mem_get_info(device)

    bytes_per_item = 62 * 1024  # 62 KB because ~62 KB per item was empirically measured
    batch_size = int(free_memory_bytes / bytes_per_item)
    exp = int(log(batch_size) / log(2))
    batch_size = 2**exp

    return max(1024, batch_size)  # Return larger of two so never smaller than 1024


def build_sweep(frange, device='cpu'):
    """Return (sweep_freqs, step_size) for a given (start, end, num_steps).

        Where sweep_freqs is an array of frequencies to be operated on
    """
    start, end, num_steps = frange
    step_size = round((end - start) / num_steps, 3)
    # Adjust the sweep range to include the last frequency
    end_adjusted = end + step_size / 10.0
    # Create sweep frequencies as a tensor on the selected device
    sweep_freqs = torch.arange(start, end_adjusted, step_size).to(device)

    return sweep_freqs


def py_torch(frange, device=None, batch_size=131_072):
    sweep_freqs = build_sweep(frange, device=device)
    # Build an array of 4094 values of M and an Fpfd tensor on device
    M = torch.arange(2, 4096, dtype=torch.int32, device=device)
    Fpfd_t = torch.tensor(Fpfd, dtype=torch.float32, device=device)

    # Run in batches to control memory use
    fmns_torch = []
    start_b = perf_counter()
    for batch in sweep_freqs.split(batch_size):
        batch_fmn = freq2fmn(batch, M, Fpfd=Fpfd_t, device=device)
        fmns_torch.append(batch_fmn)        # Creating a list of tensors
    fmns_torch = torch.cat(fmns_torch)      # Join the list of tensors into one
    elapsed = perf_counter() - start_b

    if Fpfd_t.is_cuda: # using torch.tensor side effect to find device. True=='cuda'
        peak_mem = round(torch.cuda.max_memory_allocated(device) / (1024**3), 6)
        print(line(), f'{peak_mem=} GB')
        hw_device = 'gpu'
    else:
        hw_device = 'cpu'

    num_freq_steps = round(len(sweep_freqs) / 1_000_000, 2)
    print(line(), f'Converted {num_freq_steps} million frequencies to FMN in {elapsed:.3f} sec on {hw_device}')

    return fmns_torch.cpu().numpy()


if __name__ == '__main__':
    cpus = int(cpu_count() / 2)
    print(line(), f'number of CPUs = {cpus}')

    cpu = 0     # Manually force testing on cpu vs gpu
    if cpu:
        device = 'cpu'
    else:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    frange = (23.5, 6000.0, 5_976_000)
    sz_batch = calculate_gpu_batch_size(device)
    fmns = py_torch(frange, device, sz_batch)    # Approx 2 sec on gpu and 108 sec on cpu

