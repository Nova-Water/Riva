# Connecting MYSKA Pay and NovaCore

Both integrations ship as **read-only placeholders** in this MVP
(`backend/app/tools/myska.py`, `backend/app/tools/novacore.py`). Until
configured, their tools return a clear "not yet connected" message instead
of fabricating data. This document explains how to wire up the real APIs.

## 1. Configure the environment

In `.env`:

```env
MYSKA_API_BASE_URL=https://api.myskapay.example.com
MYSKA_API_KEY=...

NOVACORE_API_BASE_URL=https://api.novacore.example.com
NOVACORE_API_KEY=...
```

`Settings.myska_configured()` / `novacore_configured()`
(`backend/app/config.py`) simply check that both the base URL and key are
set — as soon as they are, the adapter tools start making real requests
instead of returning the "not connected" message.

## 2. Match the real endpoint paths

Each adapter currently assumes a simple REST shape. Update the path
constants inside the `_myska_get` / `_novacore_get` calls in
`backend/app/tools/myska.py` and `backend/app/tools/novacore.py` to match
the real API:

```python
# backend/app/tools/myska.py
async def handle_myska_get_company_summary(_, ctx):
    result = await _myska_get(ctx, "/company/summary")  # <- update this path
    ...
```

Current placeholder paths:

| Tool | Path |
|---|---|
| `myska_get_company_summary` | `/company/summary` |
| `myska_get_incomplete_payrolls` | `/payrolls/incomplete` |
| `myska_get_employee_count` | `/employees/count` |
| `myska_get_recent_payroll_runs` | `/payrolls/recent` |
| `novacore_get_sales_summary` | `/sales/summary` |
| `novacore_get_open_invoices` | `/invoices/open` |
| `novacore_get_low_stock_items` | `/inventory/low-stock` |
| `novacore_get_recent_transactions` | `/transactions/recent` |

## 3. Match the real authentication scheme

The placeholder sends `Authorization: Bearer <API_KEY>`. If the real MYSKA
Pay or NovaCore API uses a different scheme (API key header, HMAC signing,
OAuth2 client credentials, etc.), update the `headers` dict in `_myska_get`
/ `_novacore_get` accordingly. If OAuth2 is required, add a small token
cache (fetch + refresh) inside the same module rather than re-authenticating
on every call.

## 4. Shape the response for RIVA

The adapters currently return the raw JSON response under `data`. If the
real API's response shape is large or deeply nested, consider mapping it to
a smaller, purpose-built summary before returning it from the tool handler —
this keeps what the LLM sees (and might repeat back to the user) concise and
relevant.

## 5. Keep it read-only until reviewed

Do not add write/mutating calls (creating payroll runs, editing invoices,
etc.) to these adapters without:

1. Classifying the new tool as **red** permission (see `docs/ADDING_TOOLS.md`).
2. Adding an explicit, human-readable confirmation message describing the
   real-world effect of the action.
3. Updating `docs/SECURITY.md` to reflect the new capability.

This mirrors Nova Tech's policy that RIVA must never modify payroll,
customer, sales, or inventory records without a human explicitly approving
each action.

## 6. Test against a staging environment first

Point `MYSKA_API_BASE_URL` / `NOVACORE_API_BASE_URL` at a staging or sandbox
instance while validating the integration, and confirm error handling
(`httpx.HTTPError` in the adapter) surfaces a clear, non-fatal message in
RIVA rather than a stack trace.
