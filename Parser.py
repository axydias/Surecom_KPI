from collections import OrderedDict
from os.path import join, basename, dirname, isdir
from os import mkdir
from Bands import Operators, Bands3G
from KPIs import KPI, Range, KPIPercentageSamples
from Settings import OUTPUTDIR


class Parser:
    def __init__(self, filename, operator_to_scan):
        self.filename = filename
        self.outputFile = basename(filename)[:-4] + '.csv'
        self.operator_to_scan = operator_to_scan

        # RSCP ranges
        rangesRSCP = OrderedDict()
        rangesRSCP['<-110'] = Range(-500, -110, '<= -110')
        rangesRSCP['-110to-105'] = Range(-110, -105, '-110 to -105')
        rangesRSCP['-105to-100'] = Range(-105, -100, '-105 to -100')
        rangesRSCP['-100to-95'] = Range(-100, -95, '-100 to -95')
        rangesRSCP['-95to-90'] = Range(-95, -90, '-95 to -90')
        rangesRSCP['-90to-85'] = Range(-90, -85, '-90 to -85')
        rangesRSCP['-85to-80'] = Range(-85, -80, '-85 to -80')
        rangesRSCP['-80to-75'] = Range(-80, -75, '-80 to -75')
        rangesRSCP['-75to-70'] = Range(-75, -70, '-75 to -70')
        rangesRSCP['-70to-15'] = Range(-70, -15, '-70 to -15')
        self.rscp = KPI("rsrp", rangesRSCP)

        # Ec/No ranges
        rangesEcNo = OrderedDict()
        rangesEcNo['<-13'] = Range(-50, -13, '-34 to -13')
        rangesEcNo['-13to-10'] = Range(-13, -10, '-13 to -10')
        rangesEcNo['-10to-7'] = Range(-10, -7, '-10 to -7')
        rangesEcNo['-7to-4'] = Range(-7, -4, '-7 to -4')
        rangesEcNo['-4to0'] = Range(-4, 0, '-4 to 0')
        self.ecno = KPI("rsrq", rangesEcNo)

        allBands = Bands3G[Operators[self.operator_to_scan]]

        # UARFCN ranges
        self.uarfcn = KPIPercentageSamples("earfcn", allBands)

        # Percentage for SC
        self.sc = KPIPercentageSamples('sci')

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
                    self.rscp.addSample(results[0])
                    self.ecno.addSample(results[1])
                    self.uarfcn.addSample(results[2])
                    self.sc.addSample(results[3])

        self.rscp.calculatePercentages()
        self.ecno.calculatePercentages()
        print("Parsing completed")

    def writeOutput(self):
        # Create output dir if not exists
        if not isdir(join(dirname(__file__), OUTPUTDIR)):
            mkdir(join(dirname(__file__), OUTPUTDIR))
            print("Created directory: " + join(dirname(__file__), OUTPUTDIR))

        fullOutputFilename = join(dirname(__file__), join(OUTPUTDIR, self.outputFile))
        print("Writing results to '" + fullOutputFilename + "'")
        rangesRSCP = self.rscp.printRanges()
        rangesEcNo = self.ecno.printRanges()
        rangesBand = self.uarfcn.printRanges()
        rangesSC = self.sc.printRanges()
        with open(fullOutputFilename, 'w') as outfile:
            outfile.write(Operators[self.operator_to_scan] + ":" + self.filename)
            outfile.write("\n")

            outfile.write("UMTS RSCP (dBm)\n")
            outfile.write(rangesRSCP)
            outfile.write("\n")

            outfile.write("UMTS Ec/Io (dB)\n")
            outfile.write(rangesEcNo)
            outfile.write("\n")

            outfile.write("UMTS UARFCN\n")
            outfile.write(rangesBand)
            outfile.write("\n")

            outfile.write("UMTS SC\n")
            outfile.write(rangesSC)
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
