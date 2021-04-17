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
        rangesRSRP['<-110'] = Range(-500, -110, '<= -110')
        rangesRSRP['-110to-105'] = Range(-110, -105, '-110 to -105')
        rangesRSRP['-105to-100'] = Range(-105, -100, '-105 to -100')
        rangesRSRP['-100to-95'] = Range(-100, -95, '-100 to -95')
        rangesRSRP['-95to-90'] = Range(-95, -90, '-95 to -90')
        rangesRSRP['-90to-85'] = Range(-90, -85, '-90 to -85')
        rangesRSRP['-85to-80'] = Range(-85, -80, '-85 to -80')
        rangesRSRP['-80to-75'] = Range(-80, -75, '-80 to -75')
        rangesRSRP['-75to-70'] = Range(-75, -70, '-75 to -70')
        rangesRSRP['-70to-15'] = Range(-70, -15, '-70 to -15')
        self.rsrp = KPI("rsrp", rangesRSRP)

        # RSRQ ranges
        rangesRSRQ = OrderedDict()
        rangesRSRQ['<-13'] = Range(-50, -13, '-34 to -13')
        rangesRSRQ['-13to-10'] = Range(-13, -10, '-13 to -10')
        rangesRSRQ['-10to-7'] = Range(-10, -7, '-10 to -7')
        rangesRSRQ['-7to-4'] = Range(-7, -4, '-7 to -4')
        rangesRSRQ['-4to0'] = Range(-4, 0, '-4 to 0')
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
                results = getLineAttributes(line, [5, 6, 7, 8])
                if results is not None:
                    if results[2] not in allBands:  # ignore samples from other operators
                        continue
                    self.rsrp.addSample(results[0])
                    self.rsrq.addSample(results[1])
                    self.earfcn.addSample(results[2])
                    self.sci.addSample(results[3])

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
