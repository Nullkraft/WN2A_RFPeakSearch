import time
import numpy as np



# Set up timer to call toggle_led() every 0.5 seconds
last_toggle_time = time.perf_counter()
interval = 0.2e-4

if __name__ == '__main__':
    print()
    count = 0
    while True:
        current_time = time.perf_counter()
        delta_time = current_time - last_toggle_time
        count += 1
        if delta_time > interval:
            delta_time = round(delta_time, 8)
            print(f'{delta_time = }, {int(np.floor(np.log10(delta_time)))}')
            last_toggle_time = current_time
        if count > 100:
            break

