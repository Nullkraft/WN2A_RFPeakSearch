#
# This file is part of WN2A_RFPeakSearch.
#
# This file is part of the WN2A_RFPeakSearch distribution
# (https://github.com/Nullkraft/WN2A_RFPeakSearch).
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

"""Combine two sets of sweep readings into a single calbrated chip control file.

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


class Calibrate():

    """
    Best spurs calibration class combines the best control codes from references 1 and 2.

    ...

    Attributes
    ----------
    name : dict
        calibrated_dict
    file_1 : str
        Filename of the ref1 hardware control file.
    file_2 : str
        Filename of the ref2 hardware control file.
    age : int
        age of the person

    Methods
    -------
    info(additional=""):
        Prints the person's name and age.

    """

    def __init__(self, fname: str) -> None:
        self.calibrated_dict = {}
        pass

    def combine(self, file_1: str, file_2: str) -> dict:
        """
        Public method Combine file_1 and file_2 to create the calibrated hardware control dict.

        @param file_1 Uncalibrated hardware control dict for ref_clock_1.
        @type str
        @param file_2 Uncalibrated hardware control dict for ref_clock_2.
        @type str
        @return Calibrated hardware control dictionary.
        @rtype dict

        """
        return self.calibrated_dict


if __name__ == '__main__':
    print()


    print('Calibraion complete')
