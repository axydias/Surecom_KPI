from collections import OrderedDict
from os.path import join, basename, dirname

from Stats3G import KPI, Range
from settings import OUTPUTDIR


class Parser:
    def __init__(self, filename):
        self.filename = filename
        self.outputFile = basename(filename)[:-4] + '.csv'

        # RSCP
        rangesRSCP = OrderedDict()
        rangesRSCP['<-101'] = Range(-500, -101, '<= -101')
        rangesRSCP['-94to-101'] = Range(-101, -94, '-94 to -101')
        rangesRSCP['-15to-94'] = Range(-94, -15, '-15 to -94')
        self.rscp = KPI("rscp", rangesRSCP)

        # Ec/No
        rangesEcNo = OrderedDict()
        rangesEcNo['<-15'] = Range(-50, -14, '-34 to -14')
        rangesEcNo['-15to0'] = Range(-14, 0, '-14 to 0')
        self.ecno = KPI("ecno", rangesEcNo)

        # UARFCN
        rangesBand = OrderedDict()
        rangesBand['umts900'] = Range(3063, 3064, 'UMTS 900')
        rangesBand['umts2100'] = Range(10712, 10738, 'UMTS 2100')
        self.band = KPI("band", rangesBand)

        # Read input file
        print ("Reading input file " + filename)
        with open(filename) as infile:
            for line in infile:
                if 'Time' in line:
                    continue
                results = getLineAttributes(line, [6, 7, 8])
                if results is not None:
                    self.rscp.addSample(results[0])
                    self.ecno.addSample(results[1])
                    self.band.addSample(results[2])

        self.rscp.calculatePercentages()
        self.ecno.calculatePercentages()
        self.band.calculatePercentages()
        print("Parsing completed")

    def writeOutput(self):
        fullOutputFilename = join(dirname(__file__), join(OUTPUTDIR, self.outputFile))
        print("Writing results to '" + fullOutputFilename + "'")
        rangesRSCP = self.rscp.printRanges()
        rangesEcNo = self.ecno.printRanges()
        rangesBand = self.band.printRanges()
        with open(fullOutputFilename, 'w') as outfile:
            outfile.write("UMTS RSCP (dBm)\n")
            outfile.write(rangesRSCP)
            outfile.write("\n")

            outfile.write("UMTS Ec/Io (dB)\n")
            outfile.write(rangesEcNo)
            outfile.write("\n")

            outfile.write("UMTS Band\n")
            outfile.write(rangesBand)
            outfile.write("\n")


def getLineAttributes(line, attributeList):
    line = line.split("\t")
    result = []
    for attr in attributeList:
        if attr-1 < len(line):
            if line[attr-1] == '':
                return None
            result.append(line[attr-1])
    return result
