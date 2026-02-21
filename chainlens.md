# ChainLens

A Bitcoin transaction and block parser that processes raw blockchain data and outputs structured JSON with rich metadata.

---

## Overview

ChainLens ingests raw Bitcoin data files and runs them through a **Core Parser** pipeline to deserialize, classify, and enrich transactions — producing output for both a CLI tool and a web visualizer.

```
Raw Transaction + Previous Outputs + Block Files (.dat)
                          │
                          ▼
                     Core Parser
                          │
                          ▼
                    Output Results
```

---

## Core Parser

The parser performs three main operations in parallel:

### 1. Deserialize
Decodes raw transaction bytes into structured fields:
- Version
- Inputs
- Outputs
- Witness data
- Lock time

### 2. Compute IDs
- `txid` — standard transaction ID
- `wtxid` — witness transaction ID (SegWit hash)

### 3. Classify Script Types
Identifies the locking script type for each output:
- **P2PK** — Pay to Public Key
- **P2PKH** — Pay to Public Key Hash (`1...`)
- **P2SH** — Pay to Script Hash (`3...`)
- **P2WPKH** — Pay to Witness Public Key Hash (`bc1q...`)
- **P2WSH** — Pay to Witness Script Hash (`bc1q...`, longer)
- **P2TR** — Pay to Taproot (`bc1p...`, private & flexible)
- **OP_Return** — Always 0 sats (data carrier)

### Additional Processing
- **Decode Addresses** — human-readable address strings
- **Accounting** — compute fee rate per vbyte
- **Timelocks** — absolute time + RBF (Replace-By-Fee) flags
- **Weight** — transaction weight in weight units
- **Warnings** — flag anomalies and issues

---

## Output

### CLI Tool (`cli.sh`)

```bash
# Run with fixture file
cli.sh fixture.json

# Output transaction JSON
out/<txid>.json

# Print to stdout
stdout

# Block mode
--block-mode

# Exit codes
0  # Success
1  # Error
```

### Web Visualizer

- Served via `web.sh` → `localhost`
- Paste or upload raw transaction hex
- **Story View** — who paid, cast, risks
- **Flow Diagram** — visual input/output graph
- **GET /api/health** — health check endpoint

---

## Output JSON Schema

### Key Fields

| Category | Fields |
|---|---|
| **Identity** | `txid`, `wtxid` |
| **Size** | `weight`, `vbytes` |
| **Time** | `timelocks`, `RBF` |
| **Money** | `inputs → outputs` |
| **Scripts** | `types`, `ASM` |
| **Alerts** | `warnings` |

---

## Block Parser

Handles full Bitcoin block files (`.dat.gz`):

1. **Decompress** — `.dat.gz` decompression
2. **XOR decode** — raw byte decoding
3. **Parse block header** — 80-byte header extraction
4. **Parse all transactions** — iterates every transaction in the block

---

## Script Types Reference

> How a receiver proves ownership to spend coins.

| Type | Full Name | Address Prefix |
|---|---|---|
| P2PK | Pay to Public Key | — |
| P2PKH | Pay to Public Key Hash | `1...` |
| P2SH | Pay to Script Hash | `3...` |
| P2WPKH | Pay to Witness Public Key Hash | `bc1q...` |
| P2WSH | Pay to Witness Script Hash | `bc1q...` (longer) |
| P2TR | Pay to Taproot | `bc1p...` |
| OP_Return | Data carrier | always 0 sats |

---

## File Structure

```
chainlens/
├── cli.sh                  # CLI entry point
├── web.sh                  # Web server entry point
├── fixture.json            # Test fixture
├── out/
│   └── <txid>.json         # Per-transaction output
└── blocks/
    └── *.dat.gz            # Raw block files
```
