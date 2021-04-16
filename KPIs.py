from collections import OrderedDict
from datetime import datetime
import ParserException
from Settings import SEPARATOR


class Range:
    def __init__(self, minimum, maximum, description):
        self.minimum = minimum
        self.maximum = maximum
        self.description = description
        self.count = 0
        self.percentage = 0.0


class KPI:
    def __init__(self, name, ranges):
        self.name = name
        if not isinstance(ranges, OrderedDict):
            raise ParserException("Wrong ranges type, expected OrderedDict")
        self.ranges = ranges

    def addSample(self, value):
        for r in self.ranges.keys():
            myrange = self.ranges.get(r)
            if myrange.maximum > float(value) >= myrange.minimum:
                myrange.count += 1
                break

    def calculatePercentages(self):
        total = 0
        for r in self.ranges.keys():
            myrange = self.ranges.get(r)
            total += myrange.count

        for r in self.ranges.keys():
            myrange = self.ranges.get(r)
            if total > 0:
                myrange.percentage = myrange.count / total
            else:
                myrange.percentage = 0

    def printRanges(self):
        percentages = ''
        for r in self.ranges.keys():
            myrange = self.ranges.get(r)
            mystr = '{}{}{}{}{}\n'.format(myrange.description, SEPARATOR, myrange.count, SEPARATOR, myrange.percentage)
            percentages += mystr

        return percentages


class KPIPercentage:
    def __init__(self, name):
        self.name = name
        self.samples = OrderedDict()
        self.totalTime = 0
        self.activeValue = None
        self.activeStartTime = None
        self.lastTimestamp = None

    def addSample(self, key, value):
        if key in self.samples.keys():
            self.samples[key] += value
        else:
            self.samples[key] = value
        self.totalTime += value

    def parseLine(self, timestamp, value):
        if self.activeValue is None or self.activeStartTime is None:
            self.activeValue = value
            self.activeStartTime = timestamp
            self.lastTimestamp = timestamp
        elif self.activeValue != value:
            t1 = self.activeStartTime
            t2 = self.lastTimestamp
            timestamp1 = datetime.strptime(t1, '%H:%M:%S.%f')
            timestamp2 = datetime.strptime(t2, '%H:%M:%S.%f')
            difference_in_seconds = (timestamp2 - timestamp1).total_seconds()
            self.addSample(self.activeValue, difference_in_seconds)
            self.activeStartTime = timestamp
        if timestamp != '':
            self.lastTimestamp = timestamp
        self.activeValue = value

    def flushOutput(self):
        # Flush the last value
        t1 = self.activeStartTime
        t2 = self.lastTimestamp
        timestamp1 = datetime.strptime(t1, '%H:%M:%S.%f')
        timestamp2 = datetime.strptime(t2, '%H:%M:%S.%f')
        difference_in_seconds = (timestamp2 - timestamp1).total_seconds()
        self.addSample(self.activeValue, difference_in_seconds)

    def printRanges(self):
        percentages = '{}\n'.format(self.name)
        for sample in self.samples.keys():
            mystr = '{}{}{}{}{}\n'.format(sample.key, SEPARATOR, sample[sample.key], SEPARATOR,
                                          sample[sample.key]*100.0/self.totalTime)
            percentages += mystr
        return percentages


class KPIPercentageSamples:
    def __init__(self, name, initValues=None):
        self.name = name
        self.samples = OrderedDict()
        self.totalSamples = 0
        if initValues is not None:
            for key in initValues:
                self.samples[key] = 0

    def addSample(self, key, acceptedValues=None):
        if acceptedValues is None or (acceptedValues is not None and key in acceptedValues):
            if key in self.samples.keys():
                self.samples[key] += 1
            else:
                self.samples[key] = 1
            self.totalSamples += 1

    def printRanges(self):
        percentages = '{}\n'.format(self.name)
        for sample in self.samples.keys():
            if self.totalSamples > 0:
                mystr = '{}{}{}{}{}\n'.format(sample, SEPARATOR, self.samples[sample], SEPARATOR,
                                              self.samples[sample]/self.totalSamples)
            else:
                mystr = '{}{}{}{}0.0\n'.format(sample, SEPARATOR, self.samples[sample], SEPARATOR)
            percentages += mystr
        return percentages
