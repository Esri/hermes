"""
Hermes allows users to return a standard set of information about a given
dataset.  This example shows how to get the dataset properties.
"""
import hermes
import os

if __name__ == "__main__":
    fc = r"c:\temp\scratch.gdb\somedataset"
    metadata = hermes.Paperwork(dataset=fc)
    print metadata.datasetProperties