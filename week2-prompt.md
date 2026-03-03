> Build a production-ready React TypeScript single-page application called **Coin Smith** — a Bitcoin PSBT (Partially Signed Bitcoin Transaction) builder and visualizer.
>
> **Tech stack:**
> - React 18 + TypeScript
> - Tailwind CSS
> - shadcn/ui components
> - No backend — all logic runs entirely in the browser client-side
>
> ---
>
> **All Bitcoin transaction building logic must be implemented in pure TypeScript inside the frontend.** No external Bitcoin libraries. No API calls. Everything runs in the browser.
>
> Create a `src/lib/coinsmith.ts` file that exports a single function:
>
> ```ts
> export function buildTransaction(fixture: Fixture): Report
> ```
>
> This function implements the full pipeline:
>
> **Types:**
> ```ts
> type ScriptType = 'p2pkh' | 'p2sh' | 'p2wpkh' | 'p2sh-p2wpkh' | 'p2wsh' | 'p2tr'
>
> interface UTXO {
>   txid: string
>   vout: number
>   value_sats: number
>   script_pubkey_hex: string
>   script_type: ScriptType
>   address?: string
> }
>
> interface Payment {
>   value_sats: number
>   script_pubkey_hex: string
>   script_type: ScriptType
>   address?: string
> }
>
> interface Fixture {
>   network: 'mainnet' | 'testnet'
>   utxos: UTXO[]
>   payments: Payment[]
>   change: { script_pubkey_hex: string, script_type: ScriptType, address?: string }
>   fee_rate_sat_vb: number
>   rbf?: boolean
>   locktime?: number
>   current_height?: number
>   policy?: { max_inputs?: number }
> }
>
> interface OutputItem {
>   n: number
>   value_sats: number
>   script_pubkey_hex: string
>   script_type: ScriptType
>   address: string | null
>   is_change: boolean
> }
>
> interface Report {
>   ok: boolean
>   network: string
>   strategy: string
>   selected_inputs: UTXO[]
>   outputs: OutputItem[]
>   change_index: number | null
>   fee_sats: number
>   fee_rate_sat_vb: number
>   vbytes: number
>   rbf_signaling: boolean
>   locktime: number
>   locktime_type: 'none' | 'block_height' | 'unix_timestamp'
>   psbt_base64: string
>   warnings: Array<{ code: string }>
>   error?: { code: string, message: string }
> }
> ```
>
> **Step 1 — Validate:**
> Check that network is mainnet or testnet, utxos is non-empty, each utxo has a valid 64-char hex txid, positive integer value_sats, non-empty script_pubkey_hex, and recognized script_type. Check payments is non-empty with positive values. Check fee_rate_sat_vb is positive. Throw `{ code: "INVALID_FIXTURE", message: "..." }` on any violation.
>
> **Step 2 — Estimate vbytes:**
> ```
> Overhead = 10
> Input costs:  p2pkh=148, p2sh=148, p2wpkh=68, p2sh-p2wpkh=91, p2wsh=105, p2tr=58
> Output costs: p2pkh=34,  p2sh=32,  p2wpkh=31, p2sh-p2wpkh=32, p2wsh=43,  p2tr=43
> vbytes = Math.ceil(overhead + sum(input costs) + sum(output costs))
> fee = Math.ceil(vbytes * fee_rate_sat_vb)
> ```
>
> **Step 3 — Coin selection (greedy):**
> Sort UTXOs by value_sats descending. If policy.max_inputs is set, slice to that limit. Accumulate UTXOs until total covers payments + fee (with or without change). Throw `{ code: "INSUFFICIENT_FUNDS", message: "..." }` if exhausted.
>
> **Step 4 — Two-pass change computation:**
> - Pass 1: estimate fee WITHOUT change output. Compute leftover = sum(inputs) - sum(payments) - fee_no_change
> - If leftover < 546 → no change output, feeSats = sum(inputs) - sum(payments)
> - If leftover >= 546 → Pass 2: estimate fee WITH change output. changeAmount = sum(inputs) - sum(payments) - fee_with_change
> - If changeAmount < 546 after pass 2 → fall back to no change
> - Otherwise create change output with changeAmount
>
> **Step 5 — RBF and locktime (interaction matrix):**
> ```
> rbf=true                              → nSequence = 0xFFFFFFFD
> rbf=false + locktime present          → nSequence = 0xFFFFFFFE
> otherwise                             → nSequence = 0xFFFFFFFF
>
> locktime present                      → nLockTime = locktime
> locktime absent + rbf=true + height   → nLockTime = current_height
> otherwise                             → nLockTime = 0
>
> locktime_type: nLockTime===0 → "none", <500_000_000 → "block_height", else → "unix_timestamp"
> ```
>
> **Step 6 — Build PSBT base64:**
> Construct a valid BIP-174 PSBT manually in pure TypeScript using Uint8Array and DataView. Do not use any Bitcoin library.
> - Magic: bytes `[0x70, 0x73, 0x62, 0x74, 0xff]`
> - Global map: key `0x00` → unsigned transaction (version 2, inputs, outputs, locktime), terminated with `0x00`
> - Per-input map: for segwit types (p2wpkh, p2tr, p2sh-p2wpkh) add witness_utxo (key `0x01`) with script and value as little-endian int64. For legacy (p2pkh, p2sh) add a minimal non_witness_utxo placeholder. Terminate each input map with `0x00`
> - Per-output map: each output terminated with `0x00`
> - Encode all bytes as base64 string
>
> All multi-byte integers in the transaction use little-endian encoding. Use Bitcoin varint encoding for lengths.
>
> **Step 7 — Warnings:**
> ```
> HIGH_FEE      → fee_sats > 1_000_000 OR fee_rate_sat_vb > 200
> DUST_CHANGE   → change output exists with value_sats < 546
> SEND_ALL      → no change output created
> RBF_SIGNALING → nSequence <= 0xFFFFFFFD
> ```
>
> **Step 8 — Balance assertion:**
> Assert sum(inputs) === sum(outputs) + fee_sats. Throw if not equal.
>
> Wrap the entire pipeline in try/catch. On error return `{ ok: false, error: { code, message } }`.
>
> ---
>
> **UI — Single page, dark theme**
>
> Background `#0f1117`, accent orange `#f7931a`, text `#e2e8f0`.
>
> **Sections top to bottom:**
>
> **Header** — ⛏️ Coin Smith, subtitle "PSBT Transaction Builder"
>
> **Fixture loader card** — a textarea for pasting fixture JSON (pre-populated with this sample):
> ```json
> {"network":"mainnet","utxos":[{"txid":"a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1","vout":0,"value_sats":100000,"script_pubkey_hex":"0014a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1","script_type":"p2wpkh","address":"bc1q..."}],"payments":[{"value_sats":70000,"script_pubkey_hex":"0014a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2","script_type":"p2wpkh","address":"bc1q..."}],"change":{"script_pubkey_hex":"0014a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3","script_type":"p2wpkh","address":"bc1q..."},"fee_rate_sat_vb":5,"rbf":true,"current_height":850000}
> ```
> Below the textarea a full-width orange **Build Transaction** button.
>
> **Summary stats bar** (grid of cards) showing:
> - Total inputs / total input value in sats
> - Total outputs / total output value in sats
> - Fee in sats
> - Fee rate (sat/vb)
> - Transaction size (vbytes)
> - Network
>
> **RBF + Locktime row** (two side-by-side cards):
> - RBF card: ON badge (orange) or OFF badge (gray), nSequence value in hex, one-line plain English explanation
> - Locktime card: value, type badge (none=gray, block_height=blue, unix_timestamp=purple), one-line plain English explanation
>
> **Warnings panel** — only shown when warnings exist. Each warning has an icon, bold title, and plain English description. Use amber left border styling.
>
> **Two-column layout:**
> - Left: Selected Inputs — each item shows index number, script_type badge (blue), value in green, txid:vout in monospace gray, address if present
> - Right: Outputs — each item shows index, script_type badge, value in red, address if present, and either a gray PAYMENT badge or orange CHANGE badge. Change output has a subtle orange border highlight.
>
> **PSBT section** — card with title "PSBT (base64)", monospace scrollable text box showing psbt_base64, Copy to Clipboard button in top right corner.
>
> **States:**
> - Empty state: centered coin icon, "Paste a fixture and click Build Transaction"
> - Loading state: spinner with "Building transaction..."
> - Error state: red bordered card showing error.code in bold and error.message below
>
> **UX details:**
> - Parse the textarea JSON on the fly and show a red border if it is invalid JSON
> - Disable the Build button if the textarea is empty or contains invalid JSON
> - Smooth fade-in animation when results appear
> - All satoshi values formatted with thousands separators
> - Responsive layout — stacks to single column on mobile
