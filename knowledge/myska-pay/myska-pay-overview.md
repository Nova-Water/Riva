# MYSKA Pay — Overview

MYSKA Pay is Nova Tech Ltd's payroll management platform used by client
businesses across Samoa to manage employee pay, timesheets, and payroll runs.

## Key Concepts

- **Payroll run**: A scheduled processing of employee pay for a given pay period.
- **Incomplete payroll**: A payroll run that has been started but not finalised
  (missing timesheets, unapproved hours, or pending review).
- **Employee record**: Basic employment details used for payroll calculations.

## RIVA's Access

In this version of RIVA, MYSKA Pay integration is **read-only**. RIVA can
retrieve summaries, incomplete payroll status, employee counts, and recent
payroll run history once the integration is connected via
`MYSKA_API_BASE_URL` and `MYSKA_API_KEY`.

RIVA must never modify payroll records, run payroll, or change employee pay
details. These actions are out of scope for the current release and require
a human to act directly within MYSKA Pay.
