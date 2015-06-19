"""
Allows for the easy modification of metadata on a dataset


"""
__version__ = "1.0.0"
import os
import arcpy
import tempfile
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, dump,tostring, Element
from common import HermesErrorHandler, trace
########################################################################
class MetadataWriter(object):
    """
    Allows a user to update/write to existing feature dataset metdata files
    The supported dataset types are SDE tables, SDE Feature Classes,
    shapefiles, and FGDB tables/Feature Classes.  It may support formats
    but these were the only tested use cases.

    Inputs:
       dataset - path to the table/feature class
    Error Raised:
       HermesErrorHandler

    """
    _dataset = None
    _tree = None
    _temp_xml_file = None
    _temp_workspace = None
    #----------------------------------------------------------------------
    def __init__(self, dataset):
        """Constructor"""
        if arcpy.Exists(dataset):
            self._dataset = dataset
            self._setup()
        else:
            raise HermesErrorHandler(
                {
                    "function": "__init__",
                    "line": 34,
                    "filename": "writer.py",
                    "synerror": "Dataset is missing",
                    "arc" : "Dataset is missing"
                })
    #----------------------------------------------------------------------
    def _setup(self):
        """creates a blank metadata file"""
        try:
            fd, filepath = tempfile.mkstemp(".xml",
                                            dir=self.save_location,
                                            text=True)
            self._temp_xml_file = filepath
            with os.fdopen(fd, "w") as f:
                f.write("<metadata />")
                f.close()
            del fd
            arcpy.MetadataImporter_conversion(self._dataset, filepath)
            self._tree = ElementTree()
            self._tree.parse(self._temp_xml_file)
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "_setup",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : str(arcpy.GetMessages(2))
                }
            )
    #----------------------------------------------------------------------
    @property
    def xmlfile(self):
        """gets the temporary xml file path"""
        try:
            if self._temp_xml_file is None:
                self._setup()
            return self._temp_xml_file
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                    {
                        "function": "xmlfile",
                        "line": line,
                        "filename": filename,
                        "synerror": synerror,
                        "arc" : str(arcpy.GetMessages(2))
                    }
                )
    #----------------------------------------------------------------------
    @property
    def save_location(self):
        """returns the location where the xml file is saved"""
        try:
            if self._temp_workspace is None:
                self._temp_workspace = tempfile.gettempdir()
            return self._temp_workspace
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                    {
                        "function": "save_location",
                        "line": line,
                        "filename": filename,
                        "synerror": synerror,
                        "arc" : str(arcpy.GetMessages(2))
                    }
                    )
    #----------------------------------------------------------------------
    def create(self, path, value, attributeName=None, type="text"):
        """creates a new node in the xml"""
        try:
            if type == "text":
                elem = Element(os.path.basename(path))
                elem.text = value
                elementParent = self._tree.find(os.path.dirname(path))
                elementParent.append(elem)
                return True
            elif type == "attribute" and \
                 attributeName is not None:
                element = self.tree.find(path)
                if element is not None and \
                   not attributeName in element.attrib:
                    element.set(attributeName, value)
                    return True
                else:
                    return False
            else:
                line, filename, synerror = trace()
                raise HermesErrorHandler({
                    "function": "getValue",
                    "line": line,
                    "filename": filename,
                    "synerror": "invalid type of %s" % type,
                    "arc" : str(arcpy.GetMessages(2))
                })
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler({
                "function": "getValue",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc" : str(arcpy.GetMessages(2))
            })
    #----------------------------------------------------------------------
    def delete(self, path, attributeName=None, type="text"):
        """deletes a metadata entry"""
        if self._tree is None:
            self._setup()
        element = self._tree.find(path)
        if element is not None:
            self._tree.parse(self._temp_xml_file).remove(self._tree.findall(path)[0])
            dump(self._tree)
            #self._tree.remove(element)
            return True
        return False

    #----------------------------------------------------------------------
    def insert(self, path, attributeName=None, type="text"):
        """"""
        pass
    #----------------------------------------------------------------------
    def modify(self, path, value, attributeName=None, type="text"):
        """
        Changes a text or attribute element in the xml document.  If the
        values do not exist, False is returned.  If the item is updated,
        then the value is True.

        """
        try:
            if type == "text":
                element = self.tree.find(path)
                if element is not None:
                    element.text = value
                    return True
                else:
                    return False
            elif type == "attribute" and \
                 attributeName is not None:
                element = self.tree.find(path)
                if element is not None and \
                   attributeName in element.attrib:
                    element.attrib[attributeName] = value
                    return True
                else:
                    return False
            else:
                line, filename, synerror = trace()
                raise HermesErrorHandler({
                    "function": "getValue",
                    "line": line,
                    "filename": filename,
                    "synerror": "invalid type of %s" % type,
                    "arc" : str(arcpy.GetMessages(2))
                })
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler({
                    "function": "getValue",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : str(arcpy.GetMessages(2))
                })
    #----------------------------------------------------------------------
    def getFirstValue(self, path, attributeName=None, type="text"):
        """reads an attribute of text value"""
        try:
            if type == "text":
                element = self.tree.find(path)

                return element.text if element != None else ""
            elif type == "attribute" and \
                 attributeName is not None:
                if element != None and \
                   attributeName in element.attrib:
                    return element.attrib[attributeName]
                else:
                    return ""
            else:
                line, filename, synerror = trace()
                raise HermesErrorHandler({
                            "function": "getValue",
                            "line": line,
                            "filename": filename,
                            "synerror": "invalid type of %s" % type,
                            "arc" : str(arcpy.GetMessages(2))
                        })
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler({
                "function": "getValue",
                "line": line,
                "filename": filename,
                "synerror": synerror,
                "arc" : ""#str(arcpy.GetMessages(2))
                })
    #----------------------------------------------------------------------
    def getAllValues(self, path):
        """returns all values for a given entry"""
        for elem in self._tree.findall(path):
            yield elem.text
    #----------------------------------------------------------------------
    @property
    def tree(self):
        """returns the parsed ElementTree()"""
        try:
            if self._tree is None:
                self._setup()
            return self._tree
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                    {
                        "function": "tree",
                        "line": line,
                        "filename": filename,
                        "synerror": synerror,
                        "arc" : str(arcpy.GetMessages(2))
                    }
                )
    #----------------------------------------------------------------------
    def _getTree(self):
        """"""
        pass
    #----------------------------------------------------------------------
    def saveChanges(self):
        """
        saves any changes made and pushes them back into the dataset

        Inputs:
           None
        Ouput:
           path to the dataset
        """
        writer = None
        if self._tree is None:
            self._setup()
        #val = dump(self._tree)
        xmlstr = tostring(self._tree.getroot(), method='xml')
        with open(self._temp_xml_file, 'wb') as writer:
            writer.write(xmlstr)
            writer.flush()
            writer.close()
        del writer
        self._tree = None
        return arcpy.MetadataImporter_conversion(self._temp_xml_file,
                                                 self._dataset)[0]
if __name__ == "__main__":
    ds = r"c:\temp\three.gdb\lakes"
    mdw = MetadataWriter(dataset=ds)
    path="idinfo/descript/purpose"
    print mdw.getFirstValue(path=path, type="text")
    for val in mdw.getAllValues(path):
        print val
    #mdw.modify(path, value="new purpose")
    #mdw.delete(path)
    #print mdw.getValue(path=path, type="text")
    #print mdw.save()
    print 'stop'