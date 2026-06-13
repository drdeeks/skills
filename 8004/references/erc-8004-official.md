# ERC-8004 Official Specification Summary

**Source:** https://best-practices.8004scan.io/docs/official-specification/erc-8004-official.html

## Abstract

ERC-8004 enables discovering, choosing, and interacting with agents across organizational boundaries without pre-existing trust. Trust models are pluggable and tiered, with security proportional to value at risk.

## Motivation

MCP and A2A handle agent capabilities, authentication, and task orchestration, but don't cover discovery and trust. ERC-8004 addresses this through three registries deployable as per-chain singletons.

## Identity Registry

- ERC-721 with URIStorage extension
- Global identification: `{namespace}:{chainId}:{identityRegistry}` + `agentId`
- Registration file MUST include: type, name, description, services, registrations
- Services can point to A2A agent cards, MCP endpoints, ENS names, DIDs, wallet addresses
- `agentWallet` metadata key reserved for payment address (requires EIP-712/ERC-1271 proof to change)

## Reputation Registry

- Feedback: signed fixed-point value + valueDecimals + optional tags
- Feedback submitter MUST NOT be agent owner/operator
- `feedbackHash` = KECCAK-256 of feedbackURI content (for non-IPFS)
- On-chain aggregation enables smart contract composability
- Complex reputation aggregation expected off-chain

## Validation Registry

- Agents request validation with requestURI + requestHash
- Validators respond with 0-100 response value
- Multiple responses per request (progressive validation, soft/hard finality)
- Validators can be stake-secured re-execution, zkML, or TEE oracles

## Security Considerations

- Sybil attacks possible on reputation
- Protocol makes signals public and uses same schema
- On-chain pointers/hashes cannot be deleted (audit trail)
- ERC cryptographically ensures registration file matches on-chain agent
- Cannot guarantee advertised capabilities are functional (trust models address this)
