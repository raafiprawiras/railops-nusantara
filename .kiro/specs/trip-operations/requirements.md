# Requirements — Trip Operations & Monitoring

## FR-1: Trip CRUD
- List with search (trip_number), filter (status, date, train, route), pagination
- Detail with status timeline
- Create (admin/operator)
- Edit (admin/operator)
- Delete via POST (admin only)

## FR-2: Monitoring
- Real-time-like monitoring view of active trips
- Update status with notes
- Status history timeline per trip

## FR-3: Business Rules
- trip_number unique
- origin != destination
- scheduled_arrival > scheduled_departure
- Train must be Aktif (not Tidak Aktif/Dalam Perawatan/Mengalami Gangguan)
- platform > 0, delay_minutes >= 0
- actual_arrival >= actual_departure
- Status change → TripStatusHistory record
- Tiba → actual_arrival required (auto-fill with now)
- Berangkat/Dalam Perjalanan → actual_departure required
- Dibatalkan → notes required

## FR-4: Authorization
- administrator: full CRUD + delete
- operator: view + create + edit + update status
- supervisor: view only

## FR-5: Dashboard Integration
- Real counts: trips today, on-time, delayed, cancelled
- Recent trips table from database
