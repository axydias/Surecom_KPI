from collections import OrderedDict
import ParserException
from settings import SEPERATOR


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
            myrange.percentage = myrange.count / total

    def printRanges(self):
        percentages = ''
        for r in self.ranges.keys():
            myrange = self.ranges.get(r)
            mystr = '{}{}{}{}{}\n'.format(myrange.description, SEPERATOR, myrange.count, SEPERATOR, myrange.percentage)
            percentages += mystr

        return percentages
