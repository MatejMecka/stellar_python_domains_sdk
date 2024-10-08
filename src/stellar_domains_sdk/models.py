"""
Data models for the Stellar Domains SDK.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Union

@dataclass
class SorobanDomainsSDKParams:
    """Parameters for initializing the Stellar Domains SDK."""
    rpc_url: str
    contract_id: str
    network_passphrase: str
    simulation_account: str
    default_fee: int
    default_timeout: Optional[int] = None

@dataclass
class DomainRecord:
    """Represents a domain record."""
    node: str
    owner: str
    address: str
    exp_date: int
    snapshot: int
    collateral: int

@dataclass
class SubDomainRecord:
    """Represents a subdomain record."""
    node: str
    parent: str
    address: str
    snapshot: int

DomainResult = Dict[str, Union[str, Dict[str, Any]]]
