# hermes
Collection of Utilities to Read/Write a Dataset's Metadata.
Allows users to easily create and modify the metadata from the feature
class.  The data will be returned as a dictionary object for easy of
use.  This means users can modify values and push them back into the
metadata by referencing the key names.

![futureramahermes](http://upload.wikimedia.org/wikipedia/en/c/cb/FuturamaHermesConrad.png "Source: wikimedia.org")

# Why use hermes?
Metadata is the way users describe their data.  XML is hard, but this tool
converts the XML to a Python dictionary.  This means metadata is easy to
modify, change and add.

#  Requirements
 - ArcGIS Desktop 10.3.x+
 - Python 2.7.x

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