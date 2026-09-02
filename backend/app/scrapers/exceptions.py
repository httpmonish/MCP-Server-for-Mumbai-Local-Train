class PortalException(Exception):
    """Base class for all portal-related exceptions."""
    pass

class PortalAuthError(PortalException):
    """Raised when login fails."""
    pass

PortalAuthenticationError = PortalAuthError

class PortalSelectorError(PortalException):
    """Raised when a required DOM element is not found."""
    pass

class PortalTimeoutError(PortalException):
    """Raised when a Playwright operation times out."""
    pass
