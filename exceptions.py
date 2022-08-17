class InvalidBarcodeException(Exception):
    pass

class TooFewPointsException(Exception):
    pass

class OnlyOnePointException(TooFewPointsException):
    pass

class OnlyTwoPointException(TooFewPointsException):
    pass

class NoPointsException(TooFewPointsException):
    pass