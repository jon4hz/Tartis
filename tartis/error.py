class Error(Exception):
    """Base class for other exceptions"""
    pass

class NoTakeProfitFound(Error):
    """"Raised when no take profit is found"""
    pass

class NoEntryFound(Error):
    """"Raised when no entry is found"""
    pass

class ParseError(Error):
    """ 
    Raised when message parsing failed.
    Possible failures are missmatch between Target and Percent 
    """
    pass

class NoPairFound(Error):
    """"Raised when no pair is found"""
    pass
