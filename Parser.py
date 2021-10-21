from collections import OrderedDict
from os.path import join, basename, dirname, isdir
from os import mkdir
from Bands import Operators, Bands4G
from KPIs import KPI, Range, KPIPercentageSamples
from Settings import OUTPUTDIR


class Parser:
    def __init__(self, filename, operator_to_scan):
        self.filename = filename
        self.outputFile = basename(filename)[:-4] + '.csv'
        self.operator_to_scan = operator_to_scan

        # RSRP ranges
        rangesRSRP = OrderedDict()
        rangesRSRP['<-101'] = Range(-500, -101, '<= -101')
        rangesRSRP['-101to-94'] = Range(-101, -94, '-101 to -94')
        rangesRSRP['-94to-15'] = Range(-94, -15, '-94 to -15')
        self.rsrp = KPI("rsrp", rangesRSRP)

        # RSRQ ranges
        rangesRSRQ = OrderedDict()
        rangesRSRQ['<-14'] = Range(-50, -14, '-34 to -14')
        rangesRSRQ['-14to0'] = Range(-14, 0, '-14 to 0')
        self.rsrq = KPI("rsrq", rangesRSRQ)

        allBands = Bands4G[Operators[self.operator_to_scan]]

        # EARFCN ranges
        self.earfcn = KPIPercentageSamples("earfcn", allBands)

        # Percentage for SCI
        self.sci = KPIPercentageSamples('sci')

        # Read input file
        print ("Reading input file " + filename)
        with open(filename) as infile:
            for line in infile:
                if 'Time' in line:
                    continue
                results = getLineAttributes(line, [5, 6, 7, 8], acceptEmpty=True)
                if results is not None:
                    if results[2] not in allBands:  # ignore samples from other operators
                        continue
                    self.rsrp.addSample(results[0], False)
                    self.rsrq.addSample(results[1], False)
                    self.earfcn.addSample(results[2], False)
                    self.sci.addSample(results[3], False)

        self.rsrp.calculatePercentages()
        self.rsrq.calculatePercentages()
        print("Parsing completed")

    def writeOutput(self):
        # Create output dir if not exists
        if not isdir(join(dirname(__file__), OUTPUTDIR)):
            mkdir(join(dirname(__file__), OUTPUTDIR))
            print("Created directory: " + join(dirname(__file__), OUTPUTDIR))

        fullOutputFilename = join(dirname(__file__), join(OUTPUTDIR, self.outputFile))
        print("Writing results to '" + fullOutputFilename + "'")
        rangesRSRP = self.rsrp.printRanges()
        rangesRSRQ = self.rsrq.printRanges()
        rangesEARFCN = self.earfcn.printRanges()
        rangesSCI = self.sci.printRanges()
        with open(fullOutputFilename, 'w') as outfile:
            outfile.write(Operators[self.operator_to_scan] + ":" + self.filename)
            outfile.write("\n")

            outfile.write("4G RSRP (dBm)\n")
            outfile.write(rangesRSRP)
            outfile.write("\n")

            outfile.write("4G RSRQ (dB)\n")
            outfile.write(rangesRSRQ)
            outfile.write("\n")

            outfile.write("4G EARFCN\n")
            outfile.write(rangesEARFCN)
            outfile.write("\n")

            outfile.write("4G SCI\n")
            outfile.write(rangesSCI)
            outfile.write("\n")


def getLineAttributes(line, attributeList, acceptEmpty=False):
    line = line.split("\t")
    result = []
    for attr in attributeList:
        if attr-1 < len(line):
            if line[attr-1] == '' and acceptEmpty is False:
                return None
            result.append(line[attr-1])
    return result
