"""List of exceptions for InstagramBot."""

class Error(Exception):
    """Base class for other exceptions."""
    pass

class NoSuchUserException(Error):
    """Raised when desired user does not exist."""
    def __init__(self, username):
            self.username = username
            self.message = "User {} does not exist or deleted account.".format(self.username)
            super().__init__(self.message)

class UserAccountPrivateException(Error):
    """Raised when desired user account is not public."""
    def __init__(self, username):
        self.username = username
        self.message = "User {} is private.".format(self.username)
        super().__init__(self.message)
        
class TooManyLogs(Error):
    """Raised when too many actions are taken by bot."""
    def __init__(self):
        self.message = "Too many actions. Wait or change account in config.py"
        super().__init__(self.message)