from collections import OrderedDict
from Stats3G import RSCP, Range



class Parser:
    def __init__(self, filename):
        self.filename = filename
        ranges = OrderedDict()
        ranges['<-101'] = Range(-500, -101, '<= -101')
        ranges['-94to-101'] = Range(-101, -94, '-94 to -101')
        ranges['-15to-94'] = Range(-94, -15, '-15 to -94')
        rscp = RSCP("rscp", ranges)

        with open(filename) as infile:
            for line in infile:
                rscp.addSample(-121)
                rscp.addSample(-101)
                rscp.addSample(-40)