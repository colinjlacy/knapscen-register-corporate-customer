#!/bin/bash

# Corporate Entity Registration Script - Example Execution
# This script demonstrates how to set environment variables and run the registration script
# 
# Usage: 
#   ./example_run.sh
#   or
#   bash example_run.sh
#
# DO NOT run the Python script directly with 'sh register_corporate_entity.py'
# Instead, use 'python register_corporate_entity.py' or run this example script

# Exit on any error
set -e

echo "🏢 Corporate Entity Registration Script Example"
echo "=============================================="
echo "📝 Note: Use './example_run.sh' or 'bash example_run.sh' to run this demo"
echo "🚫 Do NOT use 'sh register_corporate_entity.py' - that won't work!"
echo ""

# Company Information
export COMPANY_NAME="Example Tech Solutions"
export SUBSCRIPTION_TIER="groovy"

# Database Configuration
export DB_HOST="localhost"
export DB_PORT="33006"
export DB_USER="bassline-boogie-user"
export DB_PASSWORD="8Qd8*yZK&zIxS%!s"
export DB_NAME="bassline-boogie"

# NATS JetStream Configuration
export NATS_SERVER="nats://localhost:40953"
export NATS_STREAM="customer-onboarding"
export NATS_SUBJECT="customer-saved"
export NATS_USER="admin"
export NATS_PASSWORD="admin"

echo "📋 Configuration:"
echo "  Company: $COMPANY_NAME"
echo "  Subscription: $SUBSCRIPTION_TIER"
echo "  Database: $DB_HOST:$DB_PORT/$DB_NAME"
echo "  NATS: $NATS_SERVER"
echo "  Stream: $NATS_STREAM"
echo "  Subject: $NATS_SUBJECT"
echo ""

# Check if Python script exists
if [ ! -f "register_corporate_entity.py" ]; then
    echo "❌ Error: register_corporate_entity.py not found in current directory"
    exit 1
fi

# Check if Python is available
echo "🔍 Checking Python availability..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Error: Python is not installed or not in PATH"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Using Python command: $PYTHON_CMD"

# Check if requirements file exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found in current directory"
    exit 1
fi

# Check if requirements are installed
echo "🔍 Checking Python dependencies..."
$PYTHON_CMD -c "import mysql.connector; import nats" 2>/dev/null || {
    echo "⚠️  Warning: Dependencies not installed."
    echo "🔄 Installing dependencies from requirements.txt..."
    $PYTHON_CMD -m pip install -r requirements.txt
    echo "✅ Dependencies installed successfully!"
}

echo ""
echo "🚀 Running corporate entity registration..."
echo "📝 Command: $PYTHON_CMD register_corporate_entity.py"
echo ""

$PYTHON_CMD register_corporate_entity.py

echo ""
echo "✅ Registration process completed successfully!"
echo "🎉 Check the logs above for details about the registration and event publishing."
