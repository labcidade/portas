class ExpiredSession(Exception):
    """Exception raised for expired session."""
    def __init__(self, message="Session expired, a fresh session is needed"):
        super().__init__(message)
    
class CountBelowMinimum(Exception):
    """Exception raised for expired session."""
    def __init__(self, message="Court sentences count is below minimum, try refreshing the search"):
        super().__init__(message)
    
class MaxAttemptsReached(Exception):
    """Exception raised when maximum number of attempts is reached."""
    def __init__(self, message="Maximum number of attempts was reached"):
        super().__init__(message)
    