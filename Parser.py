from collections import OrderedDict
from os.path import join, basename, dirname, isdir
from os import mkdir
from Bands import Operators, Bands3G
from KPIs import KPI, Range
from Settings import OUTPUTDIR


class Parser:
    def __init__(self, filename, operator_to_scan):
        self.filename = filename
        self.outputFile = basename(filename)[:-4] + '.csv'
        self.operator_to_scan = operator_to_scan

        # RSCP ranges
        rangesRSCP = OrderedDict()
        rangesRSCP['<-101'] = Range(-500, -101, '<= -101')
        rangesRSCP['-94to-101'] = Range(-101, -94, '-94 to -101')
        rangesRSCP['-15to-94'] = Range(-94, -15, '-15 to -94')
        self.rscp = KPI("rscp", rangesRSCP)

        # Ec/No ranges
        rangesEcNo = OrderedDict()
        rangesEcNo['<-15'] = Range(-50, -14, '-34 to -14')
        rangesEcNo['-15to0'] = Range(-14, 0, '-14 to 0')
        self.ecno = KPI("ecno", rangesEcNo)

        # UARFCN ranges
        rangesBand = OrderedDict()
        allBands = Bands3G[Operators[self.operator_to_scan]]
        ranges_u900 = []
        ranges_u2100 = []
        for band in allBands:
            if band < 8000:
                ranges_u900.append(band)
            else:
                ranges_u2100.append(band)
        ranges_u900.sort()
        ranges_u2100.sort()
        rangesBand['umts900'] = Range(ranges_u900[0], ranges_u900[len(ranges_u900)-1]+1, 'UMTS 900')
        rangesBand['umts2100'] = Range(ranges_u2100[0], ranges_u2100[len(ranges_u2100)-1]+1, 'UMTS 2100')
        self.band = KPI("band", rangesBand)

        # Read input file
        print ("Reading input file " + filename)
        with open(filename) as infile:
            for line in infile:
                if 'Time' in line:
                    continue
                results = getLineAttributes(line, [6, 7, 8])
                if results is not None:
                    if int(results[2]) not in allBands:  # ignore samples from other operators
                        continue
                    self.rscp.addSample(results[0])
                    self.ecno.addSample(results[1])
                    self.band.addSample(results[2])

        self.rscp.calculatePercentages()
        self.ecno.calculatePercentages()
        self.band.calculatePercentages()
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

            outfile.write(Operators[self.operator_to_scan] + ":" + self.filename)
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
