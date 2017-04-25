# hermes
Collection of Utilities to Read/Write a Dataset's Metadata.
Allows users to easily create and modify the metadata from the feature
class.  The data will be returned as a dictionary object for easy of
use.  This means users can modify values and push them back into the
metadata by referencing the key names.

# Why use hermes?
Metadata is the way users describe their data.  XML is hard, but this tool
converts the XML to a Python dictionary.  This means metadata is easy to
modify, change and add.

# What inspired hermes? 
The name was inspired by Hermes Conrad from Futurama and his love of filing paperwork.
It also was developed to help people deal with metadata in the Python environment.

#  Requirements
 - ArcGIS Desktop 10.3.x+
 - Python 2.7.x (32-bit)

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
    ```xml<someelement myValue=1>i heart paperwork</someelement>```

    Results in:

    {'someelement': { '@myValue' : 1,
                      '#text' : 'i heart paperwork'
                    }
    }

Example 2:
        ```xml
        <someelement myValue=1>
          <subelement tags="fish">my value</subelement>
        </someelement>
        ```

Results:

        {'someelement': { '@myValue' : 1,
                          "subelement" : {'@tags' : "fish",
                                          '#text' : 'my value'
                                          }
                        }
        }

## Issues

Find a bug or want to request a new feature?  Please let us know by submitting an issue.

## Contributing

Esri welcomes contributions from anyone and everyone. Please see our [guidelines for contributing](https://github.com/esri/contributing).

## Licensing
Copyright 2015 Esri

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

A copy of the license is available in the repository's license file.

[](Esri Tags: hermes)
[](Esri Language: Python)​
