# -*- coding: utf-8 -*-

# Utility functions used for displaying the name and the line number
# of the source file. Requires: import sys
name = lambda: f'File "{__name__}.py",'
line = lambda: f"line {str(sys._getframe(1).f_lineno)},"

import sys
