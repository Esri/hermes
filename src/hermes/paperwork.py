"""
This module contains the working class that does the filing, and managing
of the metadata.  Much like Hermes Conrad, it loves to parse, change and
file metadata back and forth between dictionaries and xml.  The results is
an easy to use tool where users can script metadata changes without having
to parse the XML in XML format.

Requires : Python 2.7.x, ArcGIS 10.3.1
"""
__version__ = "1.0.0"
import os
import arcpy
import json
import tempfile
import xml.etree.cElementTree as ET
from common import HermesErrorHandler, trace
from collections import defaultdict
########################################################################
class Paperwork(object):
    """
    Allows users to easily create and modify the metadata from the feature
    class.  The data will be returned as a dictionary object for easy of
    use.  This means users can modify values and push them back into the
    metadata by referencing the key names.

    To use, just pass in the path of a feature class or table.  The dataset
    can be any support ArcGIS format that support metadata.

    Usage Reader Example:

      >>> fc =r"c:\temp\scratch.gdb\states"
      >>> pw = Paperwork(dataset=fc)
      >>> print pw.convert()

    Usage Update Example (add searchKeys to the metadata):

      >>> fc = r"c:\temp\scratch.gdb\states"
      >>> pw = Paperwork(dataset=fc)
      >>> val =  pw.convert()
      >>> val['metadata']['dataIdInfo']['searchKeys'] = {}
      >>> val['metadata']['dataIdInfo']['searchKeys']['keywords'] = ['states', 'USA']
      >>> pw.save(d=val)

    The dictionary results explained:

    All attributes begin with a '@' and will be inside the element tag.
    All text values will be stated as: #text : <value>
    Example:
       <someelement myValue=1>i heart paperwork</someelement>
       Results in:
       {'someelement': { '@myValue' : 1,
                         '#text' : 'i heart paperwork'
                       }
       }
    Example 2:
       <someelement myValue=1>
         <subelement tags="fish">my value</subelement>
       </someelement>
    Results in:
       {'someelement': { '@myValue' : 1,
                         "subelement" : {'@tags' : "fish",
                                         '#text' : 'my value'
                                         }
                       }
       }
    """
    _dataset = None
    _xmlText = None
    _temp_xml_file = None
    _temp_workspace = None
    #----------------------------------------------------------------------
    def __init__(self, dataset):
        """Constructor"""
        self.dataset = dataset
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
    def dataset(self):
        """get/sets the dataset metadata"""
        return self._dataset
    #----------------------------------------------------------------------
    @dataset.setter
    def dataset(self, value):
        """get/sets the dataset metadata"""
        if arcpy.Exists(value):
            self._dataset = value
            self._temp_xml_file = None
            self._temp_workspace = None
            self._xmlText = None
            self._setup()
        else:
            synerror = "dataset does not exist or cannot be accessed."
            raise HermesErrorHandler(
                {
                    "function": "dataset",
                        "line": 137,
                        "filename": "paperwork.py",
                        "synerror": synerror,
                        "arc" : synerror
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
    def __str__(self):
        """returns the xml text of a metadata file"""
        if self._temp_xml_file is None:
            self._setup()
        return open(self._temp_xml_file, 'rb').read()
    #----------------------------------------------------------------------
    @property
    def json(self):
        """returns the object as json from the xml document"""
        return json.dumps(self.convert())
    #----------------------------------------------------------------------
    def _metadata_to_dictionary(self, t):
        """ converts the xml to a dictionary object (recursivly)"""
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(self._metadata_to_dictionary, children):
                for k, v in dc.iteritems():
                    dd[k].append(v)
            d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
        if t.attrib:
            d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[t.tag]['#text'] = text
            else:
                d[t.tag] = text
        return d
    #----------------------------------------------------------------------
    def _dictionary_to_metadata(self, d):
        """ converts a dictionary to xml"""
        def _to_etree(d, root):
            if not d:
                pass
            elif isinstance(d, basestring):
                root.text = d
            elif isinstance(d, dict):
                for k,v in d.items():
                    assert isinstance(k, basestring)
                    if k.startswith('#'):
                        assert k == '#text' and isinstance(v, basestring)
                        root.text = v
                    elif k.startswith('@'):
                        assert isinstance(v, basestring)
                        root.set(k[1:], v)
                    elif isinstance(v, list):
                        for e in v:
                            _to_etree(e, ET.SubElement(root, k))
                    else:
                        _to_etree(v, ET.SubElement(root, k))
            else: assert d == 'invalid type'
        assert isinstance(d, dict) and len(d) == 1
        tag, body = next(iter(d.items()))
        node = ET.Element(tag)
        _to_etree(body, node)
        return ET.tostring(node)
    #----------------------------------------------------------------------
    def convert(self):
        """ converts an xml document to a dictionary """
        try:
            if self._temp_xml_file is None:
                self._setup()
            tree = ET.XML(text=open(self._temp_xml_file, 'rb').read())
            return self._metadata_to_dictionary(tree)
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "convert",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : str(arcpy.GetMessages(2))
                }
            )
    #----------------------------------------------------------------------
    def save(self, d=None):
        """
           commits the xml changes from the dictionary to the dataset
           If d is set to None, then dictionary from convert() will be
           used.

           Inputs:
              d - optional - either None or dictionary to be converted to
                metdata xml and applied to the dataset.
           Raises:
              HermesErrorHandler
        """
        try:
            if d is None:
                d = self.convert()
            elif isinstance(d, dict):
                res = self._dictionary_to_metadata(d)
                writer = None
                with open(self._temp_xml_file, 'wb') as writer:
                    writer.write(res)
                    writer.flush()
                    writer.close()
                del writer
                arcpy.MetadataImporter_conversion (self._temp_xml_file, self._dataset)
                if os.path.isfile(self._temp_xml_file):
                    os.remove(self._temp_xml_file)
                self._temp_xml_file = None
                self._temp_workspace = None
                self._xmlText = None
            else:
                raise Exception("Input must be of type dictionary")
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "save",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : synerror
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
                "database" : database,
                "dataType" : dataType,
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
