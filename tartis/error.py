class Error(Exception):
    """Base class for other exceptions"""
    def __init_subclass__(self, message):
        super().__init_subclass__()

class NoTakeProfitFound(Error, message=__name__):
    """"Raised when no take profit is found"""
    pass

class NoEntryFound(Error, message=__name__):
    """"Raised when no entry is found"""
    pass

class ParseError(Error, message=__name__):
    """ 
    Raised when message parsing failed.
    Possible failures are missmatch between Target and Percent 
    """
    pass

class NoPairFound(Error, message=__name__):
    """"Raised when no pair is found"""
    pass

class NoZoneFound(Error, message=__name__):
    """"Raised when no pair is found"""
    pass

class WrongExchange(Error, message=__name__):
    """"Raised when no pair is found"""
    pass