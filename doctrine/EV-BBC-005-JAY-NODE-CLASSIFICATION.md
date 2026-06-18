# EV-BBC-005 — Jay Wallet Constellation Node Classification

Status: READY

Purpose:
Boss Brenda must classify every discovered Jay-linked address before expanding the graph.

Rule:
Do not classify contracts as wallets.
Do not classify wallets as contracts.
Do not collapse Jay into a single address.

Canonical:
- Anchor wallet: 0x829adfedbe565f9885a7ea6bc78912acaef055e2
- Zora Creator Coin contract: 0x694ce46c64d9d1a5e9376a9febcf85ec05d72e9f

Node types:
wallet, contract, token, coin, exchange, experiment, other

Expansion rule:
Only expand from nodes that connect back to Jay, are not other, and have confidence >= 70.

Verdict:
Boss Brenda can now classify Jay’s graph before expanding it.
