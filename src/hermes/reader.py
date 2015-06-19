"""
"""
__version__ = "1.0.0"
import os
import arcpy
import tempfile
from xml.etree.ElementTree import ElementTree
from common import HermesErrorHandler, trace
########################################################################
class MetadataReader(object):
    """
       Takes a dataset and attempts to read the metadata associated with
       that table.  The result is a class that can parse out information as
       well as return a basic set of information (if it exists).

       Inputs:
          dataset - table or feature class to examine metadata.
       Raises:
          HermesErrorHandler
       Usage:
          >>> fc = r"c:\temp\scratch.gdb\dataset"
          >>> reader = hermes.MetadataReader(fc)
    """
    _dataset = None
    _xmlText = None
    _temp_xml_file = None
    _temp_workspace = None
    _tree = None
    #----------------------------------------------------------------------
    def __init__(self, dataset):
        """Constructor"""
        self._dataset = dataset
        self._setup()
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
    def _getElementText(self, elementPath):
        """Returns the specified element's text if it exists or an empty
        string if not."""
        try:
            element = self.tree.find(elementPath)
            return element.text if element != None else ""
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                    {
                        "function": "_getElementText",
                        "line": line,
                        "filename": filename,
                        "synerror": synerror,
                        "arc" : str(arcpy.GetMessages(2))
                    }
                )
    #----------------------------------------------------------------------
    def _getFirstElementText(self, elementPaths):
        """Returns the first found element matching one of the specified
        element paths"""
        try:
            result = ""
            for elementPath in elementPaths:
                element = self.tree.find(elementPath)
                if element != None:
                    result = element.text
                    break
            return result
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                    {
                        "function": "_getFirstElementText",
                        "line": line,
                        "filename": filename,
                        "synerror": synerror,
                        "arc" : str(arcpy.GetMessages(2))
                    }
                )
    #----------------------------------------------------------------------
    def _listElementsText(self, elementPath):
        """Returns a comma+space-separated list of the text values of all
        instances of the specified element, or an empty string if none are
        found."""
        try:
            elements = self.tree.findall(elementPath)
            if elements:
                return ", ".join([element.text for element in elements])
            else:
                return ""
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                    {
                        "function": "_listElementsText",
                        "line": line,
                        "filename": filename,
                        "synerror": synerror,
                        "arc" : str(arcpy.GetMessages(2))
                    }
                )
    #----------------------------------------------------------------------
    @property
    def originator(self):
        """gets the originator text fromt he metadata"""
        try:
            if self._dataset.lower().endswith(".shp"):
                return self._getElementText("dataIdInfo/idCredit")
            else:
                return self._getElementText("idinfo/citation/citeinfo/origin")
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                    {
                        "function": "originator",
                        "line": line,
                        "filename": filename,
                        "synerror": synerror,
                        "arc" : str(arcpy.GetMessages(2))
                    }
                )
    #----------------------------------------------------------------------
    @property
    def POC(self):
        """returns the POC from the metadata"""
        try:
            return self._getFirstElementText(("idinfo/ptcontac/cntinfo/cntperp/cntorg", # Point of contact organization (person primary contact)
                                              "idinfo/ptcontac/cntinfo/cntorgp/cntorg")) # Point of contact organization (organization primary contact)
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "POC",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : str(arcpy.GetMessages(2))
                }
            )
    #----------------------------------------------------------------------
    @property
    def abstract(self):
        """Gets the abstract for the metadata"""
        try:
            if self._dataset.lower().endswith(".shp"):
                return self._getElementText("dataIdInfo/idAbs")
            else:
                return self._getElementText("idinfo/descript/abstract")
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                    {
                        "function": "abstract",
                        "line": line,
                        "filename": filename,
                        "synerror": synerror,
                        "arc" : str(arcpy.GetMessages(2))
                    }
                )
    #----------------------------------------------------------------------
    @property
    def purpose(self):
        """gets the purpose text from the metadata"""
        try:
            if self._dataset.lower().endswith(".shp"):
                return self._getElementText("dataIdInfo/idPurp")
            else:
                return self._getElementText("idinfo/descript/purpose")
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                    {
                        "function": "purpose",
                        "line": line,
                        "filename": filename,
                        "synerror": synerror,
                        "arc" : str(arcpy.GetMessages(2))
                    }
                )
    #----------------------------------------------------------------------
    @property
    def searchKeys(self):
        """gets the searchKeys values from the metadata"""
        try:
            return self._listElementsText("dataIdInfo/searchKeys/keyword")
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "searchKeys",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : str(arcpy.GetMessages(2))
                }
            )
    #----------------------------------------------------------------------
    @property
    def themeKeys(self):
        """gets the themekey values from the metadata"""
        try:
            if self._dataset.lower().endswith(".shp"):
                return self._listElementsText("dataIdInfo/themeKeys/keyword")
            else:
                return self._listElementsText("idinfo/keywords/theme/themekey")
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                    {
                        "function": "themeKeys",
                        "line": line,
                        "filename": filename,
                        "synerror": synerror,
                        "arc" : str(arcpy.GetMessages(2))
                    }
                )
    #----------------------------------------------------------------------
    def getElementText(self, path):
        """returns the element text"""
        try:
            return self._getElementText(elementPath=path)
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "getElementText",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : str(arcpy.GetMessages(2))
                }
            )
    #----------------------------------------------------------------------
    def getListElements(self, path):
        """returns a list of elements"""
        try:
            return self._listElementsText(elementPath=path)
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "getListElements",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : str(arcpy.GetMessages(2))
                }
            )
    #----------------------------------------------------------------------
    def getFirstElementText(self, path):
        """returns the first element from a tuple of paths"""
        try:
            if isinstance(path, str):
                path = (path)
            elif isinstance(path, (tuple, list)):
                pass
            else:
                raise HermesErrorHandler("Invalid input %s" % type(path))
            return self._getFirstElementText(elementPaths=path)
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "getFirstElementText",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : str(arcpy.GetMessages(2))
                }
            )
    #----------------------------------------------------------------------
    @property
    def datasetProperties(self):
        """
        returns a collection of common dataset properties including
        information about the workspace.
        The return object is a dictionary {}
        """
        try:
            validationWorkspace = os.path.dirname(self._dataset)
            desc = arcpy.Describe(self._dataset)
            descWrksp = arcpy.Describe(desc.path)
            database, owner, tableName = [i.strip() if i.strip() != "(null)" else "" \
                                          for i in arcpy.ParseTableName(desc.name,
                                                                        validationWorkspace).split(",")]
            datasetType = desc.datasetType if hasattr(desc, "datasetType") else ""
            workspaceFactoryProgID = descWrksp.workspaceFactoryProgID if hasattr(descWrksp, "workspaceFactoryProgID") else ""
            workspaceType = descWrksp.workspaceType if hasattr(descWrksp, "workspaceType") else ""
            connectionString = descWrksp.connectionString if hasattr(descWrksp, "connectionString") else ""
            alias = desc.aliasName if hasattr(desc, "aliasName") else ""
            dataType = descWrksp.dataType if hasattr(descWrksp, "dataType") else ""
            return {
                "owner" : owner,
                "tableName" : tableName,
                "alias" : alias,
                "datasetType" : datasetType,
                "workspace" : {
                    "type" : descWrksp.dataType,
                    "path" : desc.path,
                    "connectionString" : connectionString,
                    "workspaceType" : workspaceType,
                    "workspaceFactoryProgID" : workspaceFactoryProgID
                }
            }
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "datasetProperties",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : str(arcpy.GetMessages(2))
                }
            )
if __name__ == "__main__":
    mdr = MetadataReader(dataset=r"c:\temp\scratch.gdb\state")
    print mdr.datasetProperties
