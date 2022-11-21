# WN2A_RFPeakSearch
This is the pyqt application for controlling and plotting the output of the 3GHz Spectrum Analyzer.

The 3GHz Spectrum Analyzer was designed by Mike Masterson, WN2A using an ADF4356 for LO1 and two MAX2871's for LO2 and LO3. The output of either LO2 or LO3 is fed to the input of a LogAmp which produces an output voltage in the range 0-to-2.3 VDC. The output is digitized and converted to dBm for display in this Python program. The graph that is produced is the amplitude of every frequency found from 1MHz to 3GHz.


Plotting with pyqtplot using OpenGL & Experimental settings:
  If you want the plot to have a nice pan-&-zoom experience then you will need to install OpenGL and enable the experimental setting. This combination makes PlotCurveItem() use PyOpenGL when drawing.

  Activate your virtual environment:
    ~ cd %project folder%
    ~ source bin/activate
    ~ pip install pyopengl

  Edit your PyQt mainWindow.py file:
    import pyqtgfaph as pg

  In the __init__() of class MainWindow.py:
    pg.setConfigOptions(useOpenGL=True, enableExperimental=True)

