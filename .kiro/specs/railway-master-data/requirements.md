# Requirements — Railway Master Data

## Functional Requirements

### FR-1: Train CRUD
- List with search, status filter, pagination
- Detail view
- Create (administrator only)
- Edit (administrator only)
- Delete via POST (administrator only)
- Confirmation modal before delete

### FR-2: Station CRUD
- List with search, status filter, pagination
- Detail view
- Create (administrator only)
- Edit (administrator only)
- Delete via POST (administrator only)
- Confirmation modal before delete

### FR-3: Authorization
- All pages require login
- administrator: full CRUD
- operator/supervisor: read only (list + detail)

### FR-4: Validation
- Train: train_code unique & required, train_name required, capacity > 0, carriage_number required
- Station: station_code unique & required, station_name required, city required, province required, platform_count >= 1

### FR-5: UX
- Flash messages on success/error
- Empty state when no data
- Badge status with colors
- Breadcrumb navigation
- Pagination with query params (page, search, status)

## Non-Functional Requirements
- Server-side validation, no AJAX
- CSRF on all forms
- DELETE via POST method
- Consistent URL pattern
