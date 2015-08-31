import hermes
if __name__ == "__main__":
    fc = r"c:\data_and_maps\usa\census\blkgrp.sdc\blkgrp"
    paperwork = hermes.Paperwork(dataset=fc)
    data = paperwork.convert()
    for k,v in data.iteritems():
        print k, v