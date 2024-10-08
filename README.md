# Stellar Domains SDK

A Python SDK for interacting with Soroban Domains on the Stellar network. This package provides a simple interface to interact with domain names on the Stellar blockchain.

## Installation

```bash
pip install stellar-domains-sdk
```

## Quick Start

```python
from stellar_domains_sdk import SorobanDomainsSDK, SorobanDomainsSDKParams

# Initialize the SDK
params = SorobanDomainsSDKParams(
    rpc_url="https://soroban-testnet.stellar.org",
    contract_id="your_contract_id",
    network_passphrase="testnet",
    simulation_account="your_account",
    default_fee=100
)

sdk = SorobanDomainsSDK(params)

# Search for a domain
try:
    result = sdk.search_domain("example.xlm")
    print(f"Domain owner: {result['value']['owner']}")
except Domain404Error:
    print("Domain not found")
```

## Features

- Domain name parsing and searching
- Support for both main domains and subdomains
- Full integration with Soroban smart contracts
- Comprehensive error handling
- Type hints for better IDE support

## API Reference

### SorobanDomainsSDKParams

Parameters for initializing the SDK:

- `rpc_url`: Soroban RPC endpoint URL
- `contract_id`: The contract ID for the domains contract
- `network_passphrase`: Network passphrase ("testnet" or "public")
- `simulation_account`: Account used for simulating transactions
- `default_fee`: Default fee for transactions
- `default_timeout`: Optional timeout value for transactions

### SorobanDomainsSDK Methods

#### search_domain(domain: str, sub_domain: Optional[str] = None)

Searches for a domain or subdomain on the Stellar network.

Returns a dictionary containing domain information:
- For main domains: owner address, expiration date, collateral amount, etc.
- For subdomains: parent domain, address, snapshot data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
