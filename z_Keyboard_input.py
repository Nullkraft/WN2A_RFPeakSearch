import os
import threading
import time
import pynput

class main_prog:
    def __init__(self):
        self.loop_running = threading.Event()
        self.double_previous = threading.Event()
        self.start_all_threads()
    
    def start_loop(self, num_to_go): 
        self.loop_running.set()
        for i in range(num_to_go):
            if not self.loop_running.is_set():
                break
            print(i)
            time.sleep(1)
            if self.double_previous.is_set():
                print('Double of the previous value is {}'.format(2*i))
                self.double_previous.clear()
        
        # Stops listening to keyboard events
        #self.listener.stop() # Not needed if the process is just about to end
        os._exit(0)
    
    def start_all_threads(self):
        if not self.loop_running.is_set():
            x = int(input('How far you want the count to go: '))
            
            # Collect keyboard events in a non-blocking fashion
            self.listener = pynput.keyboard.Listener(on_press=self.on_press)
            self.listener.start()
            
            t1 = threading.Thread(target=self.start_loop, args=[x])
            t1.start()
            t1.join()
    
    def on_press(self, key):
        # print(key)
        try:
            if key.char == 'q':
                self.loop_running.clear()
            elif key.char == 'd':
                self.double_previous.set()
        except AttributeError:
            pass

if __name__ == '__main__':
    main_prog()
