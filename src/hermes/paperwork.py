"""
This module contains the working class that does the filing, and managing
of the metadata.  Much like Hermes Conrad, it loves to parse, change and
file metadata back and forth between dictionaries and xml.  The results is
an easy to use tool where users can script metadata changes without having
to parse the XML in XML format.

Requires : Python 2.7.x, ArcGIS 10.3.1


Copyright 2015 Esri
Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
__version__ = "1.1.0"
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
            if isinstance(d, dict):
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
                return True
            else:
                raise Exception("Input must be of type dictionary")
            return False
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
    def exportToXML(self, outFolder=None, outName=None):
        """
        Exports a metadata file (.xml) to a save location and a given name.
        To get the save changes, call the save() before running the
        function.

        Example:
        >>> fc = r"c:\temp\scratch.gdb\states"
        >>> pw = Paperwork(dataset=fc)
        >>> val =  pw.convert()
        >>> val['metadata']['dataIdInfo']['searchKeys'] = {}
        >>> val['metadata']['dataIdInfo']['searchKeys']['keywords'] = ['states', 'USA']
        >>> pw.save(d=val)
        >>> print pw.exportToXML(r"c:\temp\mymetadata", "system_shell.xml")

        Inputs:
          outFolder - optional - is the value provided is not given, then
           systems temp folder will be used.
          outName - optional - is the name of the xml file.  This can be
           provided, or created by the system.  The file create will be
           randomly generated.
        Output:
           path to xml file
        """
        try:
            if outFolder is None:
                outFolder = tempfile.gettempdir()
            elif not outFolder is None:
                if os.path.isdir(outFolder) == False:
                    os.makedirs(outFolder)
            else:
                outFolder = tempfile.gettempdir()
            if not outName is None:
                if outName.lower().endswith('.xml'):
                    fullPath = os.path.join(outFolder, outName)
                else:
                    fullPath = os.path.join(outFolder, outName + ".xml")
            else:
                from uuid import uuid4
                fullPath = os.path.join(outFolder, uuid4().get_hex() + ".xml")
            d = self.convert()
            res = self._dictionary_to_metadata(d)
            writer = None
            with open(fullPath, 'wb') as writer:
                writer.write(res)
                writer.flush()
                writer.close()
            del writer
            return fullPath
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "exportToXML",
                    "line": line,
                    "filename": filename,
                    "synerror": synerror,
                    "arc" : synerror
                }
            )
    #----------------------------------------------------------------------
    def importXMLFile(self, xmlFile):
        """
        imports an xml metadata file to the target dataset.
        Input:
           xmlFile - the xml file to import to the dataset.
        Output:
           outputs the dictionary of the newly imported file. It returns
           None if the xml file is not valid or does not exist.
        """
        if os.path.isfile(xmlFile) and \
           xmlFile.lower().endswith(".xml"):
            arcpy.MetadataImporter_conversion(source=xmlFile,
                                              target=self.dataset)
            self._setup()
            return self.convert()
        return None
    #----------------------------------------------------------------------
    def setSyncMethod(self, method="ALWAYS"):
        """
        Automatically updates an ArcGIS item's metadata with the current
        properties of the item.
        For example, if the metadata describes the item as having one
        projection but the item's projection has changed since the last
        automatic update, the old projection information in the metadata
        will be replaced with the new projection information.

        By default, metadata is automatically updated when anyone who has
        write access to the ArcGIS item views its metadata. Metadata can
        also be synchronized by running this tool. The option to turn off
        synchronization when you view metadata doesn't affect how this tool
        operates.

        Inputs:
           method - The type of synchronization that will take place.
            ALWAYS -Properties of the source item are always added to or
             updated in its metadata. Metadata will be created if it
             doesn't already exist. This is the deault.
            ACCESSED -Properties of the source item are added to or updated
             in its metadata when it is accessed. Metadata will be created
             if it doesn't already exist.
            CREATED -Metadata will be created and properties of the source
             item will be added to it if the item doesn't already have
             metadata.
            NOT_CREATED -Properties of the source item are added to or
             updated in existing metadata.
            OVERWRITE -The same as "ALWAYS" except all information that can
             be recorded automatically in the metadata will be recorded.
             Any properties typed in by a person will be replaced with the
             item's actual properties.
            SELECTIVE -The same as "OVERWRITE" except the title and the
             content type will not be overwritten with default values for
             the item. Used when metadata is upgraded to the ArcGIS 10.x
             metadata format.
           Ouput:
             dataset path
        """
        try:
            methods = ["ALWAYS", "CREATED", "NOT_CREATED",
                       "OVERWRITE", "SELECTIVE", "ACCESSED"]

            if method.upper() in methods:
                arcpy.SynchronizeMetadata_conversion(source=self._dataset,
                                                     synctype=method)
                return self.dataset
            else:
                raise Exception("Invalid method type: %s" % method)
        except:
            line, filename, synerror = trace()
            raise HermesErrorHandler(
                {
                    "function": "setSyncMethod",
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
