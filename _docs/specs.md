# TableQ — Restaurant Waitlist Manager

## Overview

TableQ is a restaurant waitlist management tool. A hostess manages the waitlist
and table assignments from a control screen; guests check their own status
remotely via a personal QR-linked page (read-only).

## Users

- **Hostess** — manages the waitlist, tables, and seating. No login required
  (MVP: single shared, unauthenticated screen for one restaurant).
- **Guest** — no account. Receives a unique QR code/link when added to the
  waitlist and uses it to check their live status. Cannot edit anything.

## Core entities

### Table

- Configured in advance (fixed list, not editable by hostess during service).
- Fields: table number/name, capacity (seats).
- Table states: `free`, `occupied`.
- Freeing a table: the system reminds/suggests when a table is likely free
  (e.g. after an average meal duration), but the hostess must manually confirm
  before it becomes available again.

### Waitlist entry (guest party)

- Fields: guest name, party size, phone number, notes (allergies, seating
  preferences, etc.).
- Statuses (linear flow):
  1. `waiting` — in queue
  2. `table_ready` — a suitable table is available
  3. `seated` — party has been seated
  4. `cancelled_no_show` — cancelled or didn't show up
- On creation, the system generates a unique QR code/link for the guest to
  track their own status.

## Queue behavior

- **Ordering**: not strict FIFO. The system automatically prioritizes parties
  to best match them against available tables (e.g. a party of 2 can be
  matched to a free 2-top before a larger party waiting for a 6-top opens up).
- **Estimated wait time**: calculated automatically per party, based on
  historical average wait/table-turnover times, not manually entered.
- **Table assignment**: driven by matching party size to available table
  capacity, factoring into the prioritization above.

## Guest-facing view (via QR link)

- Read-only page showing:
  - Current status (`waiting` / `table_ready` / `seated` / `cancelled_no_show`)
  - Estimated wait time (while `waiting`)
- Updates live/near-live (polling or push) — no SMS integration.

## Hostess-facing view

- Waitlist screen: list of parties with name, party size, phone, notes,
  status, estimated wait, and generated QR code.
- Table board: fixed list of tables with current state (`free` / `occupied`)
  and a prompt/reminder to confirm when a table is likely free again.
- Actions: add party to waitlist, mark table ready, seat party, cancel/no-show
  a party, confirm a table is free again.
- **Daily stats view**: average wait time, number of parties seated, number
  of no-shows — for the current day.

## Explicitly out of scope (MVP)

- SMS/push notifications to guest phones
- Hostess authentication/accounts
- Multiple restaurants/locations (multi-tenancy)
- Dynamic table editing by hostess during service (adding/removing tables)
- Historical analytics beyond the current day

## Tech notes (per homework workflow)

- Frontend prototype first, with mocked backend calls centralized in one
  module.
- Backend: FastAPI, mock database first, tests written before implementation.
- Database: SQLAlchemy, database-agnostic, swapped in after frontend/backend
  integration is verified.
