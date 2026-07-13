# NovaCore — Overview

NovaCore is Nova Tech Ltd's business management platform covering sales,
inventory, and invoicing for client businesses.

## Key Concepts

- **Sales summary**: Aggregated sales performance over a period.
- **Open invoice**: An invoice that has been issued but not yet paid.
- **Low stock item**: An inventory item at or below its reorder threshold.
- **Transaction**: A recorded sale, refund, or stock adjustment.

## RIVA's Access

NovaCore integration in this version of RIVA is **read-only**. RIVA can
retrieve sales summaries, open invoices, low-stock items, and recent
transactions once connected via `NOVACORE_API_BASE_URL` and
`NOVACORE_API_KEY`.

RIVA must never create, modify, delete, or submit transactions, invoices,
or inventory records through NovaCore in this release.
