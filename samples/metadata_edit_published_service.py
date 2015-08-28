"""
Hermes allows users to update and edit published services on ArcGIS Server
This example will show how users can import data from the local shapefile
to the service.
"""

import hermes
import os

if __name__ == "__main__":
    service = r"GIS Servers\agsconnection\Hosted\USStatesBlue.MapServer"
    sourceFC = r"c:\temp\states.shp"
    #  Access each dataset's metadata
    #
    serviceMD = hermes.Paperwork(dataset=service)
    fcMD = hermes.Paperwork(dataset=sourceFC)
    #  Convert the local FC to the dictionary
    localMetadata = fcMD.convert()
    #  Load the local FC metadata into the Hosted Feature Service
    serviceMD.save(d=localMetadata)
    del serviceMD
    del fcMD
    del localMetadata
