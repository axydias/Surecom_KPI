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
        rangesRSCP['<-110'] = Range(-500, -110, '<= -110')
        rangesRSCP['-105to-110'] = Range(-110, -105, '-105 to -110')
        rangesRSCP['-100to-105'] = Range(-105, -100, '-100 to -105')
        rangesRSCP['-95to-100'] = Range(-100, -95, '-95 to -100')
        rangesRSCP['-90to-95'] = Range(-95, -90, '-90 to -95')
        rangesRSCP['-85to-90'] = Range(-90, -85, '-85 to -90')
        rangesRSCP['-80to-85'] = Range(-85, -80, '-80 to -85')
        rangesRSCP['-75to-80'] = Range(-80, -75, '-75 to -80')
        rangesRSCP['-70to-75'] = Range(-75, -70, '-70 to -75')
        rangesRSCP['-15to-70'] = Range(-70, -15, '-15 to -70')
        self.rscp = KPI("rscp", rangesRSCP)

        # Ec/No ranges
        rangesEcNo = OrderedDict()
        rangesEcNo['<-13'] = Range(-50, -13, '-34 to -13')
        rangesEcNo['-13to-10'] = Range(-13, -10, '-13 to -10')
        rangesEcNo['-10to-7'] = Range(-10, -7, '-10 to -7')
        rangesEcNo['-7to-4'] = Range(-7, -4, '-7 to -4')
        rangesEcNo['-4to0'] = Range(-4, 0, '-4 to 0')
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
