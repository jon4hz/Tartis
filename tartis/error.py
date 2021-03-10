class TartisError(Exception):
    """Base class for other exceptions"""
    def __init__(self, message):
        super().__init__(message)


