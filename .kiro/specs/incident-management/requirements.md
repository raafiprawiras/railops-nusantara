# Requirements — Incident Management

## FR-1: Incident CRUD
- List with search, filter (status, priority, type, date), pagination
- Create (admin, operator)
- Detail with status timeline
- Edit (admin, operator)
- Update status with transition validation

## FR-2: Status Transitions
- Dilaporkan → Dalam Penanganan → Selesai → Ditutup
- No skipping: Ditutup only after Selesai
- Selesai requires resolution_notes + resolved_at
- Every change recorded in IncidentStatusHistory

## FR-3: Authorization
- administrator: full access
- operator: create, edit, update status (except Ditutup)
- supervisor: view + close (Selesai → Ditutup)
- No delete (audit integrity)

## FR-4: Dashboard
- Active incident count (Dilaporkan + Dalam Penanganan)
- Recent incidents table with priority badges
