# ****** All The FreeBASIC Translations ******

def calculateRegisterValues():
    print("Solving reg values\n")


# sub Fraction_Opt 'Enter with FracT, leave with Fracc , MOD1
def Fraction_Opt():
#    Initial = 2
#    #print "From Fraction_Opt Fract= ";Fract
#    for MOD1 in range(4095, 2, -1):                  #    for MOD1 = 4095 to 2 step -1
#        Fracc = int(FracT * MOD1)
#        FracErr = abs(FracT - (Fracc/MOD1))
#        if (FracErr <= Initial):
#          NewFracc = Fracc
#          Initial = FracErr
#          NewMOD1 = MOD1
#
#    MOD1 = NewMOD1
#    Fracc = NewFracc
    pass


# End def Fraction_Opt


def doMath():
#    for registerNum in range(0, 6):
#        divider = 2**registerNum
#        
#        # Main: label
#        if (Frf * divider) >= 3000:     # Greater than 3GHz?
#            Range = registerNum
#            Fvco = divider * Frf
#            N = 1e6 * (Fvco / (Fpfd))   # Why FB using parens? Truncate a float?
#            NI = int(N)
#            FracT = N - NI
#            if FracOpt = "f": then Fraction_Opt     # goto JumpMod
#                FvcoEst=Fpfd*(1e-6)*(NI+(Fracc/MOD1))
#                FrfEst=FvcoEst/(Div)
#                #print "N= ";N;" NI= ";NI;" Fracc= ";Fracc;" MOD1= ";MOD1;" Fpfd= ";Fpfd
#                #print "FcvoEst= ";FvcoEst;"[MHz]    FrfEst= ";FrfEst;"[MHz]   FerrEst= ";int((1e6)*(FrfEst-Frf));"[Hz]"
#                restore Datarow1 # Restore Data Pointer 1
#
#                for registerNum = 0 to 5 : read Reg(registerNum, nSteps) : next 'Initialize Reg(registerNum, nSteps) default decimal Values
#
#                # These DON'T use registerNum but are hard coded as register number N for a damn reason!
#                Reg(0,nSteps) = (NI*(2^15))+(Fracc*(2^3))
#                Reg(1,nSteps) = (2^29)+(2^15)+(MOD1*(2^3))+1
#                Reg(4,nSteps) = 1670377980+((2^20)*Range)
#
#            else: MOD1=4095 : Fracc=int(FracT*MOD1)
#            # JumpMod: label
#            FvcoEst = Fpfd * (1e-6) * (NI + (Fracc/MOD1))
#            FrfEst = FvcoEst/(Div)
    pass
        
        
#' Math is called once for each step in the frequency sweep function
#sub math   # Enter with Fpfd, Frf, registerNum >> Leave with Reg(registerNum, nSteps)
#  for registerNum = 0 to 6  # Determine divider range
#    Div=(2^registerNum)
#    if (Frf*Div) >= 3000 then goto Main
#    else next
#
# Main:  Divider range now known
#      Range = registerNum : Fvco=Div*Frf
#      #Print "  Fvco= ";Fvco;" [MHz] Divider Ratio=";Div;" Frf= ";Frf;" [MHz]  Range= ";Range
#      N=1e6*(Fvco/(Fpfd))
#      NI=int(N)
#      FracT=N-NI
#      if FracOpt="f" then Fraction_Opt : goto JumpMod
#        MOD1=4095 : Fracc=int(FracT*MOD1)
#    JumpMod:
#      FvcoEst=Fpfd*(1e-6)*(NI+(Fracc/MOD1))
#      FrfEst=FvcoEst/(Div)
#      #print "N= ";N;" NI= ";NI;" Fracc= ";Fracc;" MOD1= ";MOD1;" Fpfd= ";Fpfd
#      #print "FcvoEst= ";FvcoEst;"[MHz]    FrfEst= ";FrfEst;"[MHz]   FerrEst= ";int((1e6)*(FrfEst-Frf));"[Hz]"
#      restore Datarow1 # Restore Data Pointer 1
#
#      for registerNum = 0 to 5 : read Reg(registerNum, nSteps) : next 'Initialize Reg(registerNum, nSteps) default decimal Values
#
#      # These DON'T use registerNum but are hard coded as register number N for a damn reason!
#      Reg(0,nSteps) = (NI*(2^15))+(Fracc*(2^3))
#      Reg(1,nSteps) = (2^29)+(2^15)+(MOD1*(2^3))+1
#      Reg(4,nSteps) = 1670377980+((2^20)*Range)
#
#end sub
