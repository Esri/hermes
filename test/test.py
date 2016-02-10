from __future__ import print_function
import hermes

pw = hermes.Paperwork(dataset=r"C:\temp\scratch.gdb\parcels_no_flood") # passed
print( pw.json) # passed
print( pw.dataset) # passed
print( pw.datasetProperties) # passed
print( pw.xmlfile) # passed
print( pw.save_location) # passed
pw.dataset = r"C:\temp\scratch.gdb\parcels_no_flood" # passed
val = pw.convert() # passed
pw.save() # passed
pw.save(d=val) # passed
try:
    pw.dataset = None # raised error, passed
    print ("no error, this is incorrect")
except:
    print ('error raised, all is well with pw.dataset = None')
try:
    pw.save(d="TESTdafsdalfsdkafjs") # passed raised error
    print ("no error, this is incorrect")
except:
    print ('error raised, all is well with pw.save(d="TESTdafsdalfsdkafjs")')