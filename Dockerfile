# Multi-stage build for Corporate Entity Registration Script
FROM python:3.11-alpine as builder

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-alpine

# Create non-root user for security
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application files
COPY register_corporate_entity.py .
COPY database_schema.sql .

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Make sure scripts in .local are usable
ENV PATH=/home/appuser/.local/bin:$PATH

# Add Python path
ENV PYTHONPATH=/home/appuser/.local/lib/python3.11/site-packages

# Set entrypoint
ENTRYPOINT ["python", "register_corporate_entity.py"]

# Add labels for metadata
LABEL org.opencontainers.image.title="Corporate Entity Registrar"
LABEL org.opencontainers.image.description="Python script for registering corporate entities with database and NATS JetStream integration"
LABEL org.opencontainers.image.vendor="KubeCon NATS Workflows"
LABEL org.opencontainers.image.licenses="MIT"
