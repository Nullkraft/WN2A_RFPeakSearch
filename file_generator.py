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


from hardware_cfg import cfg
import command_processor as cmd
import sys

def line() -> str:
    """
    Function Utility to simplify print debugging.

    @return The line number of the source code file.
    @rtype str

    """
    return f'line {str(sys._getframe(1).f_lineno)},'


name = f'File \"{__name__}.py\",'


class data_generator():
    """ These files will be used by calibrate_sa.py for creating the
        control dictionaries needed by the calibration scripts.
    """
    ref1 = cmd.ref_clock1_enable
    ref2 = cmd.ref_clock2_enable

    # RFin_list contains every frequency from 0 to 3000.001 MHz in 1 kHz steps
    RFin_list = cfg.RFin_list         # Test this redundant line: I think it sped things up

    def load_list(self, file_name, data_type) -> list:
        """
        Function Load the control codes for LO1, LO2 or LO3 into their associated lists.

        @param Name of a file and the data type contained in the file.
        @type File name as <class 'string'> and data type as <class 'type'> e.g. int, float, etc.
        @return A list containing the value(s) of 'type'
        @rtype <class 'list'>

        """
        with open(file_name, 'r') as f:
            tmp_list = [data_type(x) for x in f]
        return tmp_list

    def write_dict(self, file_name: str, ctrl_dict: dict) -> None:
        """
        Function Saves the contents of a unit control dictionary to file
        
        @param file_name Name of the file to save the dictionary into
        @type <class 'str'>
        @param dict A dictionary where key=RFin and a tuple as value=(ref, LO1_n, LO2_fmn)
        @type <class 'dict'>
        """
        with open(file_name, 'w') as f:
            f.write("RFin ref LO1_N LO2_FMN\n")   # Header: what the data is used for.
            for freq, data in ctrl_dict.items():
                RFin = str(freq)
                ref = str(data[0])
                LO1_n = str(data[1])
                LO2_fmn = str(data[2])
                f.write(RFin + ' ' + ref + ' ' + LO1_n + ' ' + LO2_fmn + '\n')

    def create_data(self) -> None:
        # Create the list of LO1 frequencies when using reference clock 1.
        hw = cfg()  # WTF??? Why?
        self.LO1_ref1_freq_list = [cfg.LO1_frequency(hw, RFin, cfg.Fpfd1) for RFin in self.RFin_list]
        self.LO1_ref1_freq_list = [round(x, 9) for x in self.LO1_ref1_freq_list]
        # Create the list of LO1 frequencies when using reference clock 2.
        self.LO1_ref2_freq_list = [cfg.LO1_frequency(hw, RFin, cfg.Fpfd2) for RFin in self.RFin_list]
        self.LO1_ref2_freq_list = [round(x, 9) for x in self.LO1_ref2_freq_list]
        # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 1
        self.LO1_ref1_N_list = [int(LO1_freq/cfg.Fpfd1) for LO1_freq in self.LO1_ref1_freq_list]
        # Create the list of LO1 N values for setting the frequency of the ADF4356 chip when using reference clock 2
        self.LO1_ref2_N_list = [int(LO1_freq/cfg.Fpfd2) for LO1_freq in self.LO1_ref2_freq_list]
        # Create the frequency lookup tables for LO1
        self.LO1_ref1_freq_dict = dict(zip(self.RFin_list, self.LO1_ref1_freq_list))
        self.LO1_ref2_freq_dict = dict(zip(self.RFin_list, self.LO1_ref2_freq_list))
        # Create the frequency lookup tables for LO2. (LO2_freq = LO1 - freq + cfg.IF2)
        self.LO2_ref1_freq_list = [self.LO1_ref1_freq_dict[RFin] - RFin + cfg.IF2 for RFin in self.RFin_list]
        self.LO2_ref2_freq_list = [self.LO1_ref2_freq_dict[RFin] - RFin + cfg.IF2 for RFin in self.RFin_list]
        # Create the LO2 control codes for setting the frequency of the MAX2871 chip for ref clocks 1 and 2
        self.LO2_ref1_fmn_list = [cfg.MHz_to_fmn(LO2_freq, cfg.ref_clock_1) for LO2_freq in self.LO2_ref1_freq_list]
        self.LO2_ref2_fmn_list = [cfg.MHz_to_fmn(LO2_freq, cfg.ref_clock_2) for LO2_freq in self.LO2_ref2_freq_list]

    def save_data_files(self) -> None:
        """Save LO1 and LO2 data for ref1 and ref2."""
        file_list = ["LO1_ref1_freq_steps.csv", "LO1_ref2_freq_steps.csv",
                     "LO1_ref1_N_steps.csv", "LO1_ref2_N_steps.csv",
                     "LO2_ref1_fmn_steps.csv", "LO2_ref2_fmn_steps.csv",
                     ]
        lists_list = [self.LO1_ref1_freq_list, self.LO1_ref2_freq_list,
                      self.LO1_ref1_N_list, self.LO1_ref2_N_list,
                      self.LO2_ref1_fmn_list, self.LO2_ref2_fmn_list,
                      ]
        for file_name, data_list in zip(file_list, lists_list):
            with open(file_name, 'w') as f:
                for data in data_list:
                    f.write(str(data) + '\n')
        """
        Save LO2 frequency files for ref1 and ref2.
        The data in these two lists require rounding before storing to file.
        """
        file_list.clear()
        lists_list.clear()
        file_list = ["LO2_ref1_freq_steps.csv", "LO2_ref2_freq_steps.csv"]
        lists_list = [self.LO2_ref1_freq_list, self.LO2_ref2_freq_list]
        for file_name, data_list in zip(file_list, lists_list):
            with open(file_name, 'w') as f:
                for data in data_list:
                    f.write(str(round(data, 9)) + '\n')

    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    def create_ref1_control_file(self) -> None:
        LO1_n = self.load_list('LO1_ref1_N_steps.csv', int)          # For sweeping. Convert N from a string to int
        LO2_fmn = self.load_list('LO2_ref1_fmn_steps.csv', int)      # For sweeping. Convert fmn from string to int
        full_sweep_step_dict = {freq: (self.ref1, LO1, LO2) for freq, LO1, LO2 in zip(cfg.RFin_list, LO1_n, LO2_fmn)}
        self.write_dict('full_control_ref1.csv', full_sweep_step_dict)

    def create_ref2_control_file(self):
        LO1_n = self.load_list('LO1_ref2_N_steps.csv', int)          # For sweeping. Convert N from a string to int
        LO2_fmn = self.load_list('LO2_ref2_fmn_steps.csv', int)      # For sweeping. Convert fmn from string to int
        full_sweep_step_dict = {freq: (self.ref2, LO1, LO2) for freq, LO1, LO2 in zip(cfg.RFin_list, LO1_n, LO2_fmn)}
        self.write_dict('full_control_ref2.csv', full_sweep_step_dict)

#    full_sweep_freq_dict = {freq:(self.ref2, LO1, LO2) for freq, LO1, LO2 in zip(RFin, LO1_freq_list, LO2_freq_list)}
    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""


if __name__ == '__main__':
    print()
    import time
    print(f'Fpfd values are {cfg.Fpfd1} & {cfg.Fpfd2}')

    dg = data_generator()

    start = time.perf_counter()
    dg.create_data()
    dg.save_data_files()
    dg.create_ref1_control_file()
    dg.create_ref2_control_file()
    print(f'Time to generate all the files = {round(time.perf_counter()-start, 6)} seconds')

    print("Generator done")
