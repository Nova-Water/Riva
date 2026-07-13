# RIVA AI — Security Model

## Permission Levels

Every tool in the registry (`backend/app/tools/registry.py`) declares a
`permission_level`. The agent enforces this server-side — the LLM's own
classification of a tool call is never trusted.

- **Green** — runs immediately, no confirmation. Reserved for read-only,
  non-destructive operations: system status, approved file search/read,
  opening an approved app/website, knowledgebase search, read-only business
  data.
- **Amber** — requires user confirmation before running. Used for actions
  that create local state but don't affect anything external: creating a
  document, saving a draft email, preparing a quotation.
- **Red** — always requires explicit confirmation and is reserved for
  higher-impact actions. **No red-permission tool ships executable in this
  MVP** — sending email, submitting forms, payroll changes, payments,
  credential changes, and shutdown/restart are intentionally out of scope
  (see "Current Security Limitations" below). The framework supports adding
  them later behind the same confirmation gate.

Confirmations are single-use and expire after 120 seconds
(`backend/app/security/confirmation.py`), so a stale approval can't be
replayed.

## File Allowlists

`backend/app/security/path_validation.py` resolves every requested path and
checks it against the configured allowed roots
(`RIVA_ALLOWED_FILE_ROOTS`, plus the app's own documents-output and
knowledge directories). Any path that resolves outside those roots —
including `..` traversal attempts — is rejected before the filesystem is
touched. `create_document` additionally restricts output to `.txt`/`.md`
and requires a separate confirmation to overwrite an existing file.

## Application Allowlists

`open_application` never receives an executable path from the LLM. It only
accepts an alias (`notepad`, `browser`, `calculator`, `file explorer`,
`MYSKA Pay`, `NovaCore`, or any alias added via `RIVA_ALLOWED_APPLICATIONS`),
which is mapped to a fixed launch command in
`backend/app/security/app_allowlist.py`. Unknown aliases are rejected.

## URL Validation

`open_website` and `browser_read_page` validate every URL through
`backend/app/security/url_validation.py`: only `http`/`https` are allowed;
`file:`, `javascript:`, `data:`, and other dangerous schemes are blocked;
links to executable file extensions are rejected; an optional trusted-domain
allowlist can further restrict what's reachable.

## API Key Protection

- API keys are read only from environment variables / `.env` on the backend
  (`backend/app/config.py`) and are never sent to the Electron renderer.
- All AI and voice requests are proxied through the backend — the frontend
  never talks to an LLM or TTS provider directly.
- `config_status` and settings responses only ever expose masked values
  (e.g. `settings.masked()`), never full keys.
- `backend/app/logging_config.py` runs every log line through a redaction
  filter that masks API keys, bearer tokens, voice IDs, and passwords before
  they reach the console or the rotating log file.
- The CORS policy (`backend/app/main.py`) only allows the Electron app's own
  origins, and the backend binds to `127.0.0.1` by default — it is not
  exposed to the network.

## Tool Validation

Every tool call from the LLM is parsed into a strict schema
(`backend/app/agent/schemas.py`) before anything runs:

- Unknown tool names are rejected (`ToolRegistry.get`).
- Arguments are validated against the tool's Pydantic input model
  (`ToolRegistry.validate_arguments`); invalid or unexpected fields are
  rejected.
- Malformed or non-JSON LLM output is caught (`AgentResponseParseError`)
  and surfaced as a graceful error instead of being executed.
- Tool execution is wrapped so a handler exception is always converted into
  a `ToolResult(success=False, ...)` rather than crashing the agent loop or
  being reported to the user as a false success.

## Current Security Limitations

This MVP intentionally does **not** implement, and has no code path for:

- Automatic payments or credential changes
- Automatic email sending (drafts are saved locally only)
- Unrestricted shell/PowerShell/Command Prompt execution
- File deletion or overwrite without a separate explicit confirmation
- Payroll processing or editing payroll/customer records
- Software installation
- Remote access to other computers
- Always-listening/wake-word audio capture (audio is only captured while the
  user is actively holding/toggling push-to-talk)
- Facial recognition or other surveillance features

The confirmation store is in-process memory, not persisted across backend
restarts — a pending confirmation is lost (safely, not silently approved) if
the backend restarts before the user responds. MYSKA Pay and NovaCore
adapters are read-only by design; there is no code path in this release that
allows RIVA to write to either system.
