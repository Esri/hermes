"""
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

from __future__ import absolute_import
from __future__ import print_function
import traceback
import sys
import os
from .version import __version__

def trace():
    """
        trace finds the line, the filename
        and error message and returns it
        to the user
    """

    tb = sys.exc_info()[2]
    info = sys.exc_info()
    extracttb = traceback.extract_tb(info[2])
    fileName = os.path.basename(extracttb[0][0])
    tbinfo = traceback.format_tb(tb)[0]
    # script name + line number
    line = tbinfo.split(", ")[1]
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, fileName, synerror
#--------------------------------------------------------------------------
class HermesErrorHandler(Exception):
    """Error handler for hermes package"""
    pass
#--------------------------------------------------------------------------
def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)
#--------------------------------------------------------------------------
def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj).encode('unicode_escape')


