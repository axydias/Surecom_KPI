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
        rangesRSCP['<-101'] = Range(-500, -101, '<= -101')
        rangesRSCP['-101to-94'] = Range(-101, -94, '-101 to -94')
        rangesRSCP['-94to-15'] = Range(-94, -15, '-94 to -15')
        self.rscp = KPI("rscp", rangesRSCP)

        # Ec/No ranges
        rangesEcNo = OrderedDict()
        rangesEcNo['<-14'] = Range(-50, -14, '-34 to -14')
        rangesEcNo['-14to0'] = Range(-14, 0, '-14 to 0')
        self.ecno = KPI("ecno", rangesEcNo)

        allBands = Bands3G[Operators[self.operator_to_scan]]

        # UARFCN ranges
        self.uarfcn = KPIPercentageSamples("uarfcn", allBands)

        # Percentage for SC
        self.sc = KPIPercentageSamples('sc')

        # Read input file
        print ("Reading input file " + filename)
        with open(filename) as infile:
            for line in infile:
                if 'Time' in line:
                    continue
                results = getLineAttributes(line, [6, 7, 8, 9], acceptEmpty=True)
                if results is not None:
                    if results[2] not in allBands:  # ignore samples from other operators
                        continue
                    self.rscp.addSample(results[0], False)
                    self.ecno.addSample(results[1], False)
                    self.uarfcn.addSample(results[2], False)
                    self.sc.addSample(results[3], False)

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
