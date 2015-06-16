import json
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


