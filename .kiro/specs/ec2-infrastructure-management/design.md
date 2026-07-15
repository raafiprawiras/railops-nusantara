# Design — EC2 Infrastructure Management

## Service (app/services/ec2_service.py)
```
check_health() → bool
list_instances() → list[dict]
run_instance(name, purpose, image_id, instance_type) → dict|None
start_instance(instance_id) → bool
stop_instance(instance_id) → bool
reboot_instance(instance_id) → bool
terminate_instance(instance_id) → bool
get_instance_state(instance_id) → str|None
```

## Models
### InfrastructureInstance
| Field | Type |
|-------|------|
| id | Integer PK |
| instance_id | String(30) unique |
| instance_name | String(100) |
| instance_type | String(20) |
| image_id | String(50) |
| state | String(20) |
| purpose | String(50) |
| created_by | FK users.id |
| created_at | DateTime |
| updated_at | DateTime |
| terminated_at | DateTime nullable |

### AuditLog
| Field | Type |
|-------|------|
| id | Integer PK |
| user_id | FK users.id |
| action | String(50) |
| resource_type | String(50) |
| resource_id | String(100) |
| description | Text |
| metadata_json | Text nullable |
| created_at | DateTime |

## Routes
| Method | URL | Roles |
|--------|-----|-------|
| GET | /infrastructure/ec2 | all |
| POST | /infrastructure/ec2/create | admin |
| POST | /infrastructure/ec2/<id>/start | admin, operator |
| POST | /infrastructure/ec2/<id>/stop | admin, operator |
| POST | /infrastructure/ec2/<id>/reboot | admin, operator |
| POST | /infrastructure/ec2/<id>/terminate | admin |
| POST | /infrastructure/ec2/sync | admin, operator |
| GET | /audit-logs | all |

## Valid State Actions
| State | Allowed Actions |
|-------|----------------|
| running | stop, reboot, terminate |
| stopped | start, terminate |
| pending | (wait) |
| shutting-down | (wait) |
| terminated | (none) |
