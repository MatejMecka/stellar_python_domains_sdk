"""
Main client implementation for the Stellar Domains SDK.
"""

from typing import Optional, Dict, Any, Union
from sha3 import keccak_256
from stellar_sdk import (
    Network, TransactionBuilder, SorobanServer, scval
)
from stellar_sdk.exceptions import SorobanRpcErrorResponse

from .models import (
    SorobanDomainsSDKParams, DomainRecord, 
    SubDomainRecord, DomainResult
)
from .exceptions import (
    Domain404Error, SorobanRPCError, ValidationError
)

class SorobanDomainsSDK:
    """
    Main client class for interacting with Soroban Domains on the Stellar network.
    
    Args:
        global_params: Configuration parameters for the SDK.
    """
    
    def __init__(self, global_params: SorobanDomainsSDKParams):
        self.global_params = global_params
        self._validate_params()

    def _validate_params(self) -> None:
        """Validates the initialization parameters."""
        if not self.global_params.rpc_url:
            raise ValidationError("RPC URL is required")
        if not self.global_params.contract_id:
            raise ValidationError("Contract ID is required")

    @staticmethod
    def parse_domain(domain: str, sub_domain: Optional[str] = None) -> str:
        """
        Parse a domain name into its corresponding node value.
        
        Args:
            domain: The main domain name.
            sub_domain: Optional subdomain name.
            
        Returns:
            str: The hexadecimal representation of the domain node.
        """
        xlm_hash = keccak_256(b'xlm').digest()
        domain_hash = keccak_256(domain.encode()).digest()

        record_hasher = keccak_256()
        record_hasher.update(xlm_hash)
        record_hasher.update(domain_hash)
        record_digest = record_hasher.digest()

        if sub_domain:
            sub_record_hasher = keccak_256()
            sub_record_hasher.update(keccak_256(record_digest).digest())
            sub_record_hasher.update(keccak_256(sub_domain.encode()).digest())
            return sub_record_hasher.hexdigest()
        
        return record_hasher.hexdigest()

    def search_domain(self, domain: str, sub_domain: Optional[str] = None) -> DomainResult:
        """
        Search for a domain or subdomain on the Stellar network.
        
        Args:
            domain: The main domain name to search for.
            sub_domain: Optional subdomain name.
            
        Returns:
            Dict containing the domain or subdomain information.
            
        Raises:
            Domain404Error: If the domain is not found.
            SorobanRPCError: If there's an error with the Soroban RPC connection.
        """
        try:
            soroban_server = SorobanServer(self.global_params.rpc_url)
            network_passphrase = (
                Network.TESTNET_NETWORK_PASSPHRASE 
                if self.global_params.network_passphrase.lower() == "testnet" 
                else Network.PUBLIC_NETWORK_PASSPHRASE
            )

            domain_node = self.parse_domain(domain, sub_domain)
            
            params = scval.to_vec([
                scval.to_symbol("Record" if sub_domain is None else "SubRecord"),
                scval.to_bytes(bytes.fromhex(domain_node))
            ])

            source = soroban_server.load_account(self.global_params.simulation_account)
            transaction = (
                TransactionBuilder(
                    source_account=source,
                    network_passphrase=network_passphrase,
                    base_fee=self.global_params.default_fee
                )
                .append_invoke_contract_function_op(
                    contract_id=self.global_params.contract_id,
                    function_name="record",
                    parameters=[params]
                )
                .set_timeout(self.global_params.default_timeout or 0)
                .build()
            )

            sim_response = soroban_server.simulate_transaction(transaction)
            
            if sim_response.error:
                raise SorobanRPCError(sim_response.error)

            try:
                result = sim_response.results[0].xdr
                decoded_result = scval.from_vec(result)
                map_results = scval.from_map(decoded_result[1])
            except ValueError:
                raise Domain404Error()

            if scval.from_symbol(decoded_result[0]) == "Domain":
                return {
                    "record_type": "Domain",
                    "value": DomainRecord(
                        node=scval.from_bytes(map_results[scval.to_symbol('node')]).hex(),
                        owner=scval.from_address(map_results[scval.to_symbol('owner')]).address,
                        address=scval.from_address(map_results[scval.to_symbol('address')]).address,
                        exp_date=scval.from_uint64(map_results[scval.to_symbol('exp_date')]),
                        snapshot=scval.from_uint64(map_results[scval.to_symbol('snapshot')]),
                        collateral=scval.from_uint128(map_results[scval.to_symbol('collateral')])
                    ).__dict__
                }
            else:
                return {
                    "record_type": "SubDomain",
                    "value": SubDomainRecord(
                        node=scval.from_bytes(map_results[scval.to_symbol('node')]).hex(),
                        parent=scval.from_bytes(map_results[scval.to_symbol('parent')]).hex(),
                        address=scval.from_address(map_results[scval.to_symbol('address')]).address,
                        snapshot=scval.from_uint64(map_results[scval.to_symbol('snapshot')])
                    ).__dict__
                }

        except SorobanRpcErrorResponse as e:
            raise SorobanRPCError(f"Soroban RPC error: {str(e)}")
        except Exception as e:
            if "Domain Not Found" in str(e):
                raise Domain404Error("Domain not found")
            raise
