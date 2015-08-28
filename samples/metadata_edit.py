"""
This sample shows how to use Hermes to edit metadata
"""
import hermes
import os


if __name__ == "__main__":
    fc = r"c:\temp\scratch.gdb\sampledata"
    #  Access the item's metadata
    #
    metadata = hermes.Paperwork(dataset=fc)
    # convert the XML to a dictionary
    #
    data = metadata.convert()
    #  Make some generic changes
    #
    data['metadata']['idinfo']['descript']['abstract'] = "Hermes Was Here - changed an abstract"
    data['metadata']['idinfo']['descript']['purpose'] = "Hermes Was Here - changed purpose"
    #  Save the changes back into the metadata
    #
    metadata.save(d=data)
    del metadata