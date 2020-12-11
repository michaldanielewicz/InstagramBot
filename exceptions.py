

class Error(Exception):
    """Base class for other exceptions."""
    pass

class NoSuchUserException(Error):
    """Raised when desired user does not exist."""

    def __init__(self, username):
            self.username = username
            self.message = "User {} does not exist.".format(self.username)
            super().__init__(self.message)

class UserAccountPrivate(Error):
    """Raised when desired user account is not public."""
    pass