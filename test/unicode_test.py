from hermes import common



if __name__ == "__main__":
    test = u'aä'
    val = common.safe_str(test)
    print val
    print common.safe_unicode(val)