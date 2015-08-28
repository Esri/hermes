"""
This sample shows how users can walk a metadata structure to find the
information they need quickly.  This sample shows only the XPath to each
item in the metadata and prints it out to the screen.
"""
import hermes
import os

def listKeyValues(d, path=""):
    """ simple recursive print function to walk the metadata structure"""
    for k,v in d.iteritems():
        if path != "":
            path += "/%s" % k
        else:
            path = k
        print "Key - %s" % path
        if isinstance(v, dict):
            listKeyValues(v, path)
if __name__ == "__main__":
    arcpy.env.workspace = r"c:\temp\scratch.gdb"
    for fc in arcpy.ListFeatureClasses():
        data = hermes.Paperwork(dataset=os.path.join(arcpy.env.workspace, fc)).convert()
        listKeyValues(data)