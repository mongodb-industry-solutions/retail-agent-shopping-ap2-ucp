#!/bin/bash
set -euo pipefail

echo "=========================================="
echo "MongoDB Replica Set Setup"
echo "=========================================="
echo ""

# Detect MongoDB data directory
MONGO_DATA_DIR="/usr/local/var/mongodb"
if [ ! -d "$MONGO_DATA_DIR" ]; then
    MONGO_DATA_DIR="/data/db"
fi

if [ ! -d "$MONGO_DATA_DIR" ]; then
    echo "⚠️  Could not detect MongoDB data directory."
    echo "Please enter your MongoDB data directory path:"
    read -r MONGO_DATA_DIR
fi

echo "MongoDB Data Directory: $MONGO_DATA_DIR"
echo ""

# Check if MongoDB is currently running
if pgrep -x "mongod" > /dev/null; then
    echo "📌 MongoDB is currently running. Stopping it..."
    pkill mongod || sudo pkill mongod || echo "⚠️  Could not stop MongoDB. Please stop it manually."
    sleep 2
else
    echo "✅ MongoDB is not running"
fi

echo ""
echo "Starting MongoDB as replica set 'rs0'..."
echo "Command: mongod --replSet rs0 --dbpath $MONGO_DATA_DIR --port 27017 --fork --logpath /tmp/mongod.log"
echo ""

# Start MongoDB as replica set
if mongod --replSet rs0 --dbpath "$MONGO_DATA_DIR" --port 27017 --fork --logpath /tmp/mongod.log; then
    echo "✅ MongoDB started as replica set"
else
    echo "❌ Failed to start MongoDB"
    echo "Try manually: mongod --replSet rs0 --dbpath $MONGO_DATA_DIR --port 27017"
    exit 1
fi

sleep 3

echo ""
echo "Initializing replica set..."
echo ""

# Initialize replica set
if mongosh --eval "rs.initiate()" > /tmp/rs_init.log 2>&1; then
    echo "✅ Replica set initialized"
else
    # Check if already initialized
    if mongosh --eval "rs.status()" | grep -q "ok: 1"; then
        echo "✅ Replica set already initialized"
    else
        echo "❌ Failed to initialize replica set"
        cat /tmp/rs_init.log
        exit 1
    fi
fi

echo ""
echo "Verifying replica set status..."
mongosh --eval "rs.status().ok" --quiet

if [ "$(mongosh --eval "rs.status().ok" --quiet)" = "1" ]; then
    echo ""
    echo "=========================================="
    echo "✅ MongoDB Replica Set Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Replica Set Name: rs0"
    echo "Connection String: mongodb://localhost:27017/?replicaSet=rs0"
    echo ""
    echo "Next Steps:"
    echo "1. Restart your Mandate Ledger Service:"
    echo "   pkill -f 'uvicorn src.main:app'"
    echo "   uvicorn src.main:app --reload --port 8001"
    echo ""
    echo "2. Run the payments flow test:"
    echo "   bash tests/test_payments_flow.sh"
    echo ""
    echo "3. Check change stream logs in the server output"
    echo ""
else
    echo ""
    echo "❌ Replica set setup failed"
    echo "Please check /tmp/mongod.log for errors"
    exit 1
fi


