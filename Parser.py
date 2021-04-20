from collections import OrderedDict
from os.path import join, basename, dirname, isdir
from os import mkdir
from Bands import Operators, Bands5G
from KPIs import KPI, Range, KPIPercentageSamples
from Settings import OUTPUTDIR


class Parser:
    def __init__(self, filename, operator_to_scan):
        self.filename = filename
        self.outputFile = basename(filename)[:-4] + '.csv'
        self.operator_to_scan = operator_to_scan

        # SS RSRP ranges
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

        # SINR ranges
        rangesSINR = OrderedDict()
        rangesSINR['<0'] = Range(-50, 0, '-50 to 0')
        rangesSINR['0to6'] = Range(0, 6, '0 to 6')
        rangesSINR['6to14'] = Range(6, 14, '6 to 14')
        rangesSINR['14to20'] = Range(14, 20, '14 to 20')
        rangesSINR['20to100'] = Range(20, 100, '20 to 100')
        self.sinr = KPI("sinr", rangesSINR)

        allBands = Bands5G[Operators[self.operator_to_scan]]

        # 5G ARFCN ranges
        self.arfcn = KPIPercentageSamples("arfcn", allBands)

        # Percentage for 5G PCI
        self.pci = KPIPercentageSamples('pci')

        # Read input file
        print ("Reading input file " + filename)
        with open(filename) as infile:
            for line in infile:
                if 'Time' in line:
                    continue
                results = getLineAttributes(line, [5, 6, 7, 8, 9], acceptEmpty=True)
                if results is not None:
                    if results[2] not in allBands:  # ignore samples from other operators
                        continue
                    self.rsrp.addSample(results[0], False)
                    self.rsrq.addSample(results[1], False)
                    self.arfcn.addSample(results[2], False)
                    self.pci.addSample(results[3], False)
                    self.sinr.addSample(results[4], False)

        self.rsrp.calculatePercentages()
        self.rsrq.calculatePercentages()
        self.sinr.calculatePercentages()
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
        rangesSINR = self.sinr.printRanges()
        rangesARFCN = self.arfcn.printRanges()
        rangesPCI = self.pci.printRanges()
        with open(fullOutputFilename, 'w') as outfile:
            outfile.write(Operators[self.operator_to_scan] + ":" + self.filename)
            outfile.write("\n")

            outfile.write("5G RSRP (dBm)\n")
            outfile.write(rangesRSRP)
            outfile.write("\n")

            outfile.write("5G RSRQ (dB)\n")
            outfile.write(rangesRSRQ)
            outfile.write("\n")

            outfile.write("5G SINR (dB)\n")
            outfile.write(rangesSINR)
            outfile.write("\n")

            outfile.write("5G ARFCN\n")
            outfile.write(rangesARFCN)
            outfile.write("\n")

            outfile.write("5G PCI\n")
            outfile.write(rangesPCI)
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
