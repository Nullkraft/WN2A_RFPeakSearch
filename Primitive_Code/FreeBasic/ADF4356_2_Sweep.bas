'ADF4356_2_Sweep.bas for Spectrum Analyzer Freq Synthesis. Uses Euclid
dim shared as ulong NI, x, idx, y, Frac1
dim shared as double Fvco, Fpfd, N, FracT, RF_out
dim shared as string Reg(14), T6(14)
dim shared as integer RF_divider, Range

dim shared as double target_freq(5)
target_freq(0) = 1373.37
target_freq(1) = 2371.37
target_freq(2) = 3371.37
target_freq(3) = 4373.37
target_freq(4) = 5351.37


Setup:

kill "unit_test_generated.txt"
open "unit_test_generated.txt" for append as #1


Start:
for j = 0 to 4

    RF_out = target_freq(j)     ' RF_out is the target frequency to be set

    restore register_data       ' Accessing the data for the 13 chip registers
    for idx = 0 to 13
        read Reg(idx)
    next

    restore reg6_data           ' Accessing the data for register 6
    for idx = 0 to 6
        read T6(idx)
    next

    ' RF_out = VCO_frequency / RF_divider  : See ADF4356(Rev.A) spec sheet page 30
    ' Rarrange RF_out function to solve for VCO_freq (3400 <= F_vco <= 6800) by stepping the RF_divider value.
    for x = 0 to 6  'Determine divider range
        RF_divider = (2^x)
        if (RF_out * RF_divider) >= 3400 then
            Reg(6) = T6(x)                         'Found the RF divider range
            goto Main
        endif
    next x

Main:
    Fvco = RF_divider * RF_out
    Fpfd = 60 / 2       ' Fpfd = RefClock MHz / R
    N = Fvco / Fpfd
    NI = int(N)
    FracT = N - NI
    Frac1 = int(FracT * 2^24)

    Reg(0) = str(hex(2097152 + NI * 2^4))
    Reg(1) = str(hex(1 + Frac1 * 2^4))
    Reg(2) = str(hex(2))
    Reg(3) = str(hex(3))

Transmit:
    for y = 0 to 13
        idx = 13 - y
        print #1, Reg(idx)             ' Send to "generated results" file
    next y

next j
close #1
end


register_data:
data  "00200AC0","00B02C01","010005D2","00000003","32008984","00800025","358120F6" 'R0>>R6
data  "060000E7","15596568","0F09FCC9","00C00EBA","0061200B","000015FC","0000000D" 'R7>>R13

reg6_data:
data  "350120F6","352120F6","354120F6","356120F6","358120F6","35A120F6","35C120F6" 'R6
