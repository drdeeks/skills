# Hardware Requirements for Base Node

## Minimum Specifications
- **CPU**: 8-Core minimum (modern x86_64 or ARM64)
- **RAM**: 16 GB minimum
- **Storage**: NVMe SSD with at least 2TB capacity

## Recommended Specifications
- **CPU**: 16-Core or higher
- **RAM**: 32 GB or higher
- **Storage**: NVMe SSD 4TB+ with high IOPS

## Storage Calculation
Formula: `(2 × chain_size) + snapshot_size + 20% buffer`
- Chain size: ~1.5TB (as of 2024)
- Snapshot size: ~500GB
- Recommended: 4TB+ NVMe SSD
