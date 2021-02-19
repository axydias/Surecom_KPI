class ParserException(Exception):
    def __init__(self, message):
        if message is not None:
            super(ParserException, self).__init__(message)
