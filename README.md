# WN2A_RFPeakSearch
This is the pyqt application for controlling and plotting the output of the 3GHz Spectrum Analyzer. It primarily uses PyQt GUI, pyqtgraph, and pyserial.

The 3GHz Spectrum Analyzer was designed by Mike Masterson, [WN2A](https://www.qsl.net/wn2a/) using an ADF4356 for LO1 and two MAX2871's for LO2 and LO3. The output of either LO2 or LO3 is fed to a mixer and then to the input of a LogAmp which produces an output voltage in the range 0-to-2.5 VDC. The output is digitized and converted to dBm for display in this Python program. The graph that is produced is the amplitude (RSSI) of every frequency found from 4MHz to 3GHz.


Plotting with pyqtplot using OpenGL & Experimental settings:

  If you want the plot to have a nice pan-&-zoom experience then you will need to install OpenGL and enable the experimental setting. This combination makes PlotCurveItem() use PyOpenGL when drawing.

  Activate your virtual environment:
```
~$ cd %project_folder%
~$ source bin/activate
~$ pip install pyopengl
```

Edit your PyQt mainWindow.py file:
```
    import pyqtgraph as pg
```

In the __init__() of class MainWindow.py:
```
    pg.setConfigOptions(useOpenGL=True, enableExperimental=True)
```

# WN2A 3GHz Spectrum Analyzer

Work is progressing on a Python application that sends control codes from the PC, reads the Arduino ADC, and then receives the data from the serial port. This tends to block the main thread of the gui so a pynput keyboard listener was setup to monitor for the ESC key. If pressed it will cancel the current sweep and lesaves the current plot on screen.

There are three distinct, but ultimately related, areas of concern.

## Serial

Serial must be able to successfully read and write several kilobytes of data regardless of the speed of the controller vs. the speed of the PC.  If there are any problems with the serial it can't be allowed to block the GUI.  The ultimate goal is to perform progressive plotting but for now an entire sweep of data must be received before it can be plotted.


## GUI

The GUI *must* be responsive no matter what state the program is in. The user should never be locked out of the program while a long running process tries to run to completion. For now a long running sweep blocks the GUI unless the user presses the ESC key.


## Plotting

Plotting speed is drastically improved by doing two things;
  1) Set the configuration options pyqtgraph.setConfigOptions(useOpenGL=True, enableExperimental=True)
  2) Updating the plot with graphWidget.plot.setData(x_axis_data_list, y_axis_data_list).
If not, then plot updates become exceedingly slow beyond more than a few hundred data points.


## Controller

An Arduino UNO is being used as the main controller during development. This was a deliberate choice with the idea that the best way to find methods of optimizing for speed is to restrict development to the slowest controller around. This challenge is further enhanced by restricting the Arduino code to what is primarily found on the reference page. This forced the developers to use SPI, 2Mbit serial, bit-masking, bit-shifting, binary serial transport instead of ASCII, and to eliminate the use of the delay() function(s). To speed up the operations of the Spectrum Analyzer it was necessary to use integer steps for the LO1, reduce the number of registers to be programmed for LO2 and LO3, and to program all the frequencies related to ref1 before programming all the frequencies related to ref2.
