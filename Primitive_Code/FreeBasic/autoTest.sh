#!/bin/bash
# Heavily modifying a FreeBASIC file from Mike so I wanted
# to be able to run some automated testing to make sure I
# don't screw up the expected output.
#
# Run the FreeBASIC app with a frequency that is different
# from the results recorded in the baseline registers.txt
# file. The output should indicate that the two files have
# differences.
#
# Run a second test using the FreeBASIC app with a
# frequency that should match the recorded results in the
# baseline registers.txt file. The output should indicate
# that the two files are exactly the same.
PORT=$1
BAUD=$2
FREQ=$3

# First a little cleanup if needed
cat /dev/null > testRegisters.txt

# Compile our modified FreeBASIC program for testing
fbc -lang fblite MAX2871_Command_8_testing.bas

# Run our program with a deliberate failure.
./MAX2871_Command_8_testing $FREQ $BAUD $PORT

# Compare our modified FreeBASIC with the original
# Should see some diffs displayed.
diff -y -W 25 registers.txt testRegisters.txt
cat /dev/null > testRegisters.txt
echo

# Run our program with the same frequency setting
./MAX2871_Command_8_testing 111 $BAUD $PORT

# Compare our modified FreeBASIC with the original
# Both output files should match exactly.
diff -y -W 25 registers.txt testRegisters.txt

# Cleanup old files so we don't get false positives.
rm MAX2871_Command_8_testing testRegisters.txt
echo
