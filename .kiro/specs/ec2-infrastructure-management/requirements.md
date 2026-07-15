# Requirements — EC2 Infrastructure Management

## FR-1: EC2 Service
- Boto3 EC2 client from config (LocalStack only)
- health_check, describe_instances, run_instance, start, stop, reboot, terminate
- Normalize Boto3 response to simple dict
- Handle ClientError/EndpointConnectionError gracefully

## FR-2: Instance Lifecycle
- Create (admin only) → running
- Start (admin, operator) stopped → running
- Stop (admin, operator) running → stopped
- Reboot (admin, operator) running → running
- Terminate (admin only) → terminated
- Validate state transitions in app

## FR-3: InfrastructureInstance Model
- Track instance_id, name, type, image_id, state, purpose, created_by, timestamps, terminated_at

## FR-4: AuditLog Model
- Log every lifecycle action
- user_id, action, resource_type, resource_id, description, metadata_json

## FR-5: Authorization
- admin: all
- operator: start, stop, reboot, view
- supervisor: view only

## FR-6: Sync
- /infrastructure/ec2/sync refreshes local DB from LocalStack state

## FR-7: Dashboard
- EC2 running count from DB
- Graceful fallback when unavailable
