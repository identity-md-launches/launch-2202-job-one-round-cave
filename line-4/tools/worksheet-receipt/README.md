# Worksheet Receipt

Keep a multi-step exact calculation and replay every intermediate quantity,
dimension, direct dependency, conversion and claim later. Python 3.10+ and the
standard library only. Copy this whole folder to use it independently, offline.

From the repository root, one command shows it working:

```sh
python3 -B line-4/tools/worksheet-receipt/worksheet_receipt.py demo
```

The demo exits **0**. Hypothetical inputs of 750 MiB at 12 MiB/s, plus 1500 ms
overhead, produce exactly **64 seconds**. It replays a passing 65-second budget,
faithfully replays a failed one-minute budget, and rejects an altered intermediate
value even after the attacker recalculates the content checksum. These inputs
are examples, not observations of a network or service.

## Keep your own worksheet

`create` reads the existing Worksheet Flint JSON format from stdin:

```sh
printf '%s\n' '{"schema":"worksheet-flint/1","steps":[{"name":"distance","expression":"10 km"},{"name":"duration","expression":"2 h"},{"name":"speed","expression":"$distance / $duration","to":"m/s","expect":"5 km/h"}]}' | python3 -B line-4/tools/worksheet-receipt/worksheet_receipt.py create | python3 -B line-4/tools/worksheet-receipt/worksheet_receipt.py verify
```

Both commands exit **0**, and verification reports exact speed `25/18 m/s`.
Shell single quotes preserve literal `$` references. You can save `create`'s
stdout as a receipt and feed its bytes to `verify` later. The tool itself accepts
no file paths and writes only stdout/stderr. Use shell redirection only to paths
you choose within your workspace.

Receipts contain exactly `schema`, `sources_sha256`, `request`, `result`,
`calculation_exit` and `receipt_sha256`. Hashing uses ASCII JSON with sorted
keys and compact separators; the receipt hash excludes its own field. The source
map hashes these three fixed sibling files: `engine.py`, `worksheet_flint.py`,
`worksheet_receipt.py`. Replay requires their original bytes, checks the content
hash, recomputes the entire worksheet and compares canonical bytes. It distinguishes
booleans from numbers. JSON whitespace and object key ordering do not affect replay.

**Exit 0**: valid calculation with all supplied checks passing (including no
checks). **Exit 1**: valid calculation containing a failed claim, also when that
failed claim is faithfully replayed. **Exit 2**: invalid input, source/content
hash mismatch, recomputation mismatch or a limit exceeded. `verified: true`
means faithful replay; consult `calculation_exit` and `result.passes` for whether
the claims passed. No partial result is printed for invalid late steps.

## Worksheet grammar and limits

The request has exactly `schema: "worksheet-flint/1"` and `steps`, with 1–32
ordered steps. Each requires string `name` and `expression`, and optionally string
`to`, `expect`, `at_least`, `at_most`. Names match `[A-Za-z][A-Za-z0-9_]{0,31}`.
`$name` uses an earlier result with its exact dimensions; forward references,
cycles and duplicate names fail. Failed claims never replace computed values.
Bounds are inclusive. `to` affects display only and accepts units, not references.

Expressions support `+ - * / ^ **`, parentheses, decimal/scientific numbers and
integer powers from -12 to 12. Supported units: m, cm, mm, km, in, ft, mi; kg, g,
mg, t; s, ms, min, h, day; B, KiB, MiB, GiB; L, mL; N, J, W. Multiplication is
explicit (`2 * $distance`). `2 m^2` means `(2 m)^2`; use `2 * m^2` for two square
metres. Even zero retains its dimensions. Nonterminating decimals remain exact
fractions; no intermediate is rounded.

Requests are limited to 65,536 bytes both on stdin and after compact ASCII JSON
normalization, with at most eight JSON nesting levels. Expressions have at most
4096 characters, 256 tokens and 32 nesting levels; rational numerator/denominator
have at most 2048 bits and dimension exponents are within -256..256. Receipts are
limited to 524,288 bytes including formatted creation output and 16 nesting
levels. Duplicate JSON keys, invalid UTF-8, JSON floats, nonfinite constants and
integers longer than five characters are rejected on verification. Request
quantities must be expression strings, never JSON numbers. Unknown fields fail.

## What replay does and does not establish

This is an **unsigned consistency receipt**. Hashes detect accidental changes and
identify the exact implementation; they do not establish authorship, trustworthy
software, input accuracy, completeness of a physical model or when the receipt
was created. Someone can change both a request and all its correctly recomputed
results and make a valid new receipt. Retain a trusted external copy of the
receipt hash when identity matters. Inputs and expressions are included verbatim
and are not redacted; use public or nonsensitive quantities.

The tool reads stdin and its three fixed local source files only, with no
environment/configuration, wallet, key, network or transaction access. There is
no currency, price, uncertainty propagation, offset temperature or symbolic
solver support. Numerical receipt replay needs no coin or exchange rate.

## Checks and provenance

```sh
python3 -B -m unittest discover -s line-4/tools/worksheet-receipt -v
```

Tried locally: **10 tests passed**, including 100 seeded independent Fraction
chains, source/content mismatches, rehashed intermediate/dimension/dependency/
check/request/order forgeries, boolean-number confusion, faithful failed claims,
malformed/oversized input, inherited worksheet limits, actual CLI statuses and
absence of partial stdout. All **69 inherited Line 4 tests** passed. The demo
and documented create/verify pipeline passed, also in a standalone folder copy.
These are local observations, not independent certification.

Ordinary-file snapshots, unchanged from Worksheet Flint:

- `engine.py`: SHA-256 `c683e558cdbdf6cf73d4b32572b6fa498b80e7816483b882bf2d51adfff3062e`.
- `worksheet_flint.py`: SHA-256 `09593e0004a11aced0e7efd0d55d4ff0c44de0856bc241d460af6e500d17bb65`.

The wrapper borrows canonical receipt hashing and type-sensitive replay from
Calculation Receipt. No inherited tool was modified and no dependency installed.
