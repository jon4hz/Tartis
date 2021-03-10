class Error(Exception):
    """Base class for other exceptions"""
    pass

class NoTakeProfitFound(Error):
    """"Raised when no Take Profit is found"""
    pass

class NoEntryFound(Error):
    """"Raised when no Entry is found"""
    pass

class ParseError(Error):
    """ 
    Raised when message parsing failed.
    Possible failures are missmatch between Target and Percent 
    """
    pass