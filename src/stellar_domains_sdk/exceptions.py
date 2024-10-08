"""
Exceptions for the Stellar Domains SDK.
"""

class StellarDomainsError(Exception):
    """Base exception for all Stellar Domains SDK errors."""
    pass

class Domain404Error(StellarDomainsError):
    """Raised when a domain is not found."""
    pass

class SorobanRPCError(StellarDomainsError):
    """Raised when there's an error with the Soroban RPC connection."""
    pass

class ValidationError(StellarDomainsError):
    """Raised when input validation fails."""
    pass
