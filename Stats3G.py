from collections import OrderedDict
import ParserException


class Range:
    def __init__(self, minimum, maximum, description):
        self.minimum = minimum
        self.maximum = maximum
        self.description = description
        self.count = 0


class RSCP:
    def __init__(self, name, ranges):
        self.name = name
        if not isinstance(ranges, OrderedDict):
            raise ParserException("Wrong ranges type, expected OrderedDict")
        self.ranges = ranges

    def addSample(self, value):
        for r in self.ranges:
            if r.maximum > value >= r.minimum:
                r.count += 1
                break
