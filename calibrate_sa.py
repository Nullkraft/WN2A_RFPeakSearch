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

# -*- coding: utf-8 -*-

"""Routine to take two sets of sweep readings and combine them into a single, \
   calbrated, ref_clock, LO1, LO2, and LO3 chip control file.
Classes:
    calibrate
Functions:
    dump(object, file)
    dumps(object) -> string
    load(file) -> object
    loads(bytes) -> object
Misc variables:
    __version__
    format_version
    compatible_formats
"""

import sys


def line() -> str:
    """
    Function Utility to simplify print debugging.

    @return The line number of the source code file.
    @rtype str

    """
    return f'line {str(sys._getframe(1).f_lineno)},'


name = f'File \"{__name__}.py\",'


class calibrate():
    pass

""" ********************* This block will move to spectrumAnalyzer.py ************************* """
#LO1_freq = self.load_list(('LO1_ref1_freq_steps.csv', float))  # For plotting. Convert f from a string to float
#LO2_freq = self.load_list(('LO2_ref1_freq_steps.csv', float))  # For plotting. Convert freq from string to float
#LO1_freq = self.load_list(('LO1_ref2_freq_steps.csv', float))  # For plotting. Convert f from a string to float
#LO2_freq = self.load_list(('LO2_ref2_freq_steps.csv', float))  # For plotting. Convert freq from string to float
"""
Reading the sweep dictionary from a file
"""
#test_dict = read_dict('full_control_ref1.csv')
"""
Set the sweep range and sweep step size
"""
#user_step_dict = dict(list(full_sweep_step_dict.items())[idx_start:idx_stop:idx_step])

""" ********************************************************************************************* """

if __name__ == '__main__':
    print()

    
    print('Calibraion complete')












