# Corporate Entity Registration Script Usage

This document provides examples of how to use the corporate entity registration script.

## Environment Variables

The script requires the following environment variables to be set:

### Company Information
- `COMPANY_NAME`: Name of the corporate entity (e.g., "TechCorp Solutions")
- `SUBSCRIPTION_TIER`: Subscription tier, must be one of: `basic`, `groovy`, `far-out`

### Database Connection
- `DB_HOST`: MySQL database host (e.g., "localhost" or "mysql.example.com")
- `DB_PORT`: MySQL database port (default: 3306)
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name

### NATS JetStream Configuration
- `NATS_SERVER`: NATS server URL (e.g., "nats://localhost:4222")
- `NATS_STREAM`: JetStream stream name (e.g., "CORPORATE_EVENTS")
- `NATS_SUBJECT`: Subject for the event (e.g., "corporate.registered")

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage Examples

### Example 1: Basic Setup
```bash
# Set environment variables
export COMPANY_NAME="Acme Corporation"
export SUBSCRIPTION_TIER="basic"

export DB_HOST="localhost"
export DB_PORT="3306"
export DB_USER="app_user"
export DB_PASSWORD="secure_password"
export DB_NAME="scaffold_db"

export NATS_SERVER="nats://localhost:4222"
export NATS_STREAM="CORPORATE_EVENTS"
export NATS_SUBJECT="corporate.registered"

# Run the script
python register_corporate_entity.py
```

### Example 2: Using Docker Environment File
Create a `.env` file:
```env
COMPANY_NAME=Innovation Labs Inc
SUBSCRIPTION_TIER=far-out

DB_HOST=mysql-server
DB_PORT=3306
DB_USER=corp_admin
DB_PASSWORD=my_secure_password
DB_NAME=customer_db

NATS_SERVER=nats://nats-server:4222
NATS_STREAM=REGISTRATIONS
NATS_SUBJECT=company.new
```

Then source and run:
```bash
source .env
python register_corporate_entity.py
```

### Example 3: Kubernetes ConfigMap/Secret
In a Kubernetes environment, you can use ConfigMaps and Secrets:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: corporate-registration-config
data:
  COMPANY_NAME: "Digital Ventures LLC"
  SUBSCRIPTION_TIER: "groovy"
  DB_HOST: "mysql-service"
  DB_PORT: "3306"
  DB_NAME: "app_database"
  NATS_SERVER: "nats://nats-service:4222"
  NATS_STREAM: "EVENTS"
  NATS_SUBJECT: "corporate.entity.registered"

---
apiVersion: v1
kind: Secret
metadata:
  name: corporate-registration-secrets
type: Opaque
data:
  DB_USER: <base64-encoded-username>
  DB_PASSWORD: <base64-encoded-password>
```

## Event Payload

The script publishes a JSON event to NATS JetStream with the following structure:

```json
{
  "event_type": "corporate_entity_registered",
  "timestamp": "2024-03-15T10:30:45.123456",
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "company_name": "Acme Corporation",
  "subscription_tier": "basic",
  "source": "corporate-entity-registrar"
}
```

Note: Database and NATS connection information is excluded from the event payload for security reasons.

## Error Handling

The script provides comprehensive error handling and logging:

- **Configuration errors**: Missing or invalid environment variables
- **Database errors**: Connection issues, constraint violations
- **NATS errors**: Connection or publishing failures
- **Validation errors**: Invalid subscription tiers

All errors are logged with appropriate severity levels and the script exits with code 1 on failure.

## Logging

The script uses structured logging with timestamps. Log levels:
- `INFO`: Normal operational messages
- `ERROR`: Error conditions that cause the script to fail

Example log output:
```
2024-03-15 10:30:45,123 - __main__ - INFO - Loaded company info for: Acme Corporation
2024-03-15 10:30:45,124 - __main__ - INFO - Database config loaded for host: localhost
2024-03-15 10:30:45,125 - __main__ - INFO - NATS config loaded for server: nats://localhost:4222
2024-03-15 10:30:45,200 - __main__ - INFO - Successfully connected to MySQL database
2024-03-15 10:30:45,250 - __main__ - INFO - Successfully registered corporate entity: Acme Corporation with ID: 550e8400-e29b-41d4-a716-446655440000
2024-03-15 10:30:45,300 - __main__ - INFO - Connected to NATS server: nats://localhost:4222
2024-03-15 10:30:45,350 - __main__ - INFO - Published registration event to stream 'CORPORATE_EVENTS' with subject 'corporate.registered', sequence: 12345
2024-03-15 10:30:45,351 - __main__ - INFO - Corporate entity registration completed successfully
```

## Docker Usage

### Using the Pre-built Container Image

The script is also available as a multi-architecture Docker container image:

```bash
# Pull the latest image (replace with your actual repository)
docker pull ghcr.io/your-username/knapscen-register-corporate-customer:latest

# Run with environment variables
docker run --rm \
  -e COMPANY_NAME="Docker Test Company" \
  -e SUBSCRIPTION_TIER="groovy" \
  -e DB_HOST="your-mysql-host" \
  -e DB_PORT="3306" \
  -e DB_USER="your_user" \
  -e DB_PASSWORD="your_password" \
  -e DB_NAME="your_database" \
  -e NATS_SERVER="nats://your-nats-server:4222" \
  -e NATS_STREAM="CORPORATE_EVENTS" \
  -e NATS_SUBJECT="corporate.registered" \
  ghcr.io/your-username/knapscen-register-corporate-customer:latest
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  corporate-registrar:
    image: ghcr.io/your-username/knapscen-register-corporate-customer:latest
    environment:
      - COMPANY_NAME=Docker Compose Company
      - SUBSCRIPTION_TIER=far-out
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USER=app_user
      - DB_PASSWORD=secure_password
      - DB_NAME=scaffold_db
      - NATS_SERVER=nats://nats:4222
      - NATS_STREAM=CORPORATE_EVENTS
      - NATS_SUBJECT=corporate.registered
      - NATS_USER=admin
      - NATS_PASSWORD=admin
    depends_on:
      - mysql
      - nats

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: scaffold_db
      MYSQL_USER: app_user
      MYSQL_PASSWORD: secure_password
    volumes:
      - ./database_schema.sql:/docker-entrypoint-initdb.d/schema.sql

  nats:
    image: nats:latest
    command: ["--jetstream"]
    ports:
      - "4222:4222"
```

### Building the Image Locally

```bash
# Build for current architecture
docker build -t corporate-registrar .

# Build for multiple architectures (requires buildx)
docker buildx build --platform linux/amd64,linux/arm64 -t corporate-registrar .
```

### Kubernetes Deployment

Example Kubernetes Job deployment:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: corporate-entity-registration
spec:
  template:
    spec:
      containers:
      - name: registrar
        image: ghcr.io/your-username/knapscen-register-corporate-customer:latest
        env:
        - name: COMPANY_NAME
          value: "Kubernetes Company"
        - name: SUBSCRIPTION_TIER
          value: "groovy"
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: host
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        - name: DB_NAME
          value: "scaffold_db"
        - name: NATS_SERVER
          value: "nats://nats-service:4222"
        - name: NATS_STREAM
          value: "CORPORATE_EVENTS"
        - name: NATS_SUBJECT
          value: "corporate.registered"
      restartPolicy: Never
  backoffLimit: 3
```
