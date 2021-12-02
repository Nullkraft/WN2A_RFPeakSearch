'Testing cint() to compare the results with Python's round() function

dim shared as integer x

dim as string filename = "fb_cint.csv"

Start:

'open filename for Output as #7
'print #7, " 0.5", "0.499..."

print " Step ", "0.5 ", "Step", "0.49.."
print "------------------------------------------------"
for x = 1 to 7

  print x * 0.5, cint(x * 0.5), x * 0.4999999999999997, cint(x * 0.49)

next x
