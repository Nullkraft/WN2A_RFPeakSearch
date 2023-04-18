# -*- coding: utf-8 -*-
#
# This file is part of WN2A_RFPeakSearch.
# 
# This file is part of the WN2A_RFPeakSearch distribution (https://github.com/Nullkraft/WN2A_RFPeakSearch).
# Copyright (c) 2021 Mark Stanley.
# 
# WN2A_RFPeakSearch is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# WN2A_RFPeakSearch is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


"""
Module implementing Dialog.
"""

import sys

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QDialog

from .Ui_direct_programming import Ui_Dialog
from hardware_cfg import Cfg
import command_processor as cp


def line() -> str:
    """
    Function Utility to simplify print debugging.

    @return The line number of the source code file.
    @rtype str

    """
    return f'line {str(sys._getframe(1).f_lineno)},'


name = f"File \'{__name__}.py\',"


class Dialog(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    selected = False
    
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent)
        self.setupUi(self)
    
    @pyqtSlot()
    def on_direct_btn_step_clicked(self):
        """ Walk through the 315 MHz filter by stepping the LO2 """
        start_freq = round(self.direct_start_freq_mhz.value(), 3)
        fmn = Cfg.MHz_to_fmn(start_freq, Cfg.ref_clock_1)
        if not self.selected:
            cp.sel_LO2()
            self.selected = True
        cp.set_LO2(fmn)




        """ Get next frequency based on step size """
        step_size = round(self.direct_step_freq_mhz.value(), 3)
        next_freq = start_freq + step_size
        self.direct_start_freq_mhz.setValue(next_freq)  # Rounds to 3 places to fit the control
        


    







