#!/usr/bin/env python3
"""
Clean up test data from MongoDB.

Usage:
    python cleanup_test_data.py --run-id test_1700000000_12345
    python cleanup_test_data.py --all-tests
    python cleanup_test_data.py --older-than 7  # days
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import os

def get_db():
    """Connect to MongoDB."""
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('MONGODB_DATABASE', 'mandate_ledger')

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.server_info()
        return client[db_name]
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}", file=sys.stderr)
        sys.exit(1)

def cleanup_by_run_id(db, run_id):
    """Delete all data for a specific test run."""
    print(f"🗑️  Deleting test data for run_id: {run_id}")

    # Collections and their test identification fields
    collections_config = {
        'mandate_ledger': {'field': 'metadata.test_run_id', 'type': 'exact'},
        'api_keys': {'field': 'key_id', 'type': 'prefix'},
        'audit_log': {'field': 'metadata.test_run_id', 'type': 'exact'},
        'idempotency_records': {'field': 'agent_id', 'type': 'prefix'},
        'rate_limits': {'field': 'agent_id', 'type': 'prefix'},
        'consistency_checks': {'field': 'metadata.test_run_id', 'type': 'exact'},
    }

    total_deleted = 0

    for collection_name, config in collections_config.items():
        field = config['field']
        match_type = config['type']

        # Skip if collection doesn't exist
        if collection_name not in db.list_collection_names():
            continue

        collection = db[collection_name]

        # Build query based on match type
        if match_type == 'prefix':
            # Prefix match for IDs
            query = {field: {'$regex': f'^{run_id}'}}
        else:
            # Exact match for metadata fields
            query = {field: run_id}

        try:
            result = collection.delete_many(query)
            if result.deleted_count > 0:
                print(f"  ✅ {collection_name}: deleted {result.deleted_count} documents")
                total_deleted += result.deleted_count
        except Exception as e:
            print(f"  ⚠️  {collection_name}: error - {e}")

    print(f"✨ Total deleted: {total_deleted} documents")
    return total_deleted

def cleanup_all_tests(db):
    """Delete all test data (anything with is_test=true or test_ prefix)."""
    print("🗑️  Deleting ALL test data...")

    total_deleted = 0

    # Delete by metadata flag
    metadata_collections = ['mandate_ledger', 'audit_log', 'consistency_checks']
    for collection_name in metadata_collections:
        if collection_name not in db.list_collection_names():
            continue

        collection = db[collection_name]
        try:
            result = collection.delete_many({'metadata.is_test': True})
            if result.deleted_count > 0:
                print(f"  ✅ {collection_name}: deleted {result.deleted_count} documents")
                total_deleted += result.deleted_count
        except Exception as e:
            print(f"  ⚠️  {collection_name}: error - {e}")

    # Delete by prefix
    prefix_collections = {
        'api_keys': 'key_id',
        'idempotency_records': 'agent_id',
        'rate_limits': 'agent_id'
    }

    for collection_name, field in prefix_collections.items():
        if collection_name not in db.list_collection_names():
            continue

        collection = db[collection_name]
        try:
            result = collection.delete_many({field: {'$regex': '^test_'}})
            if result.deleted_count > 0:
                print(f"  ✅ {collection_name}: deleted {result.deleted_count} documents")
                total_deleted += result.deleted_count
        except Exception as e:
            print(f"  ⚠️  {collection_name}: error - {e}")

    print(f"✨ Total deleted: {total_deleted} documents")
    return total_deleted

def cleanup_older_than(db, days):
    """Delete test data older than N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    print(f"🗑️  Deleting test data older than {days} days (before {cutoff.isoformat()})...")

    total_deleted = 0

    query = {
        'metadata.is_test': True,
        'created_at': {'$lt': cutoff}
    }

    collections = ['mandate_ledger', 'audit_log']

    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            continue

        collection = db[collection_name]
        try:
            result = collection.delete_many(query)
            if result.deleted_count > 0:
                print(f"  ✅ {collection_name}: deleted {result.deleted_count} documents")
                total_deleted += result.deleted_count
        except Exception as e:
            print(f"  ⚠️  {collection_name}: error - {e}")

    print(f"✨ Total deleted: {total_deleted} documents")
    return total_deleted

def list_test_runs(db):
    """List all test run IDs."""
    print("📋 Test runs in database:")

    try:
        # Get distinct test run IDs
        run_ids = db.mandate_ledger.distinct(
            "metadata.test_run_id",
            {"metadata.is_test": True}
        )

        if not run_ids:
            print("  (No test runs found)")
            return

        for run_id in sorted(run_ids):
            if run_id:
                # Count documents for this run
                count = db.mandate_ledger.count_documents({
                    "metadata.test_run_id": run_id
                })
                print(f"  • {run_id} ({count} mandates)")
    except Exception as e:
        print(f"  ⚠️  Error listing test runs: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='Clean up test data from MongoDB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clean up specific test run
  python cleanup_test_data.py --run-id test_1700000000_12345

  # Clean up all test data
  python cleanup_test_data.py --all-tests

  # Clean up old test data (7+ days)
  python cleanup_test_data.py --older-than 7

  # List all test runs
  python cleanup_test_data.py --list
"""
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--run-id', help='Specific test run ID to clean up')
    group.add_argument('--all-tests', action='store_true', help='Clean up all test data')
    group.add_argument('--older-than', type=int, metavar='DAYS',
                       help='Clean up test data older than N days')
    group.add_argument('--list', action='store_true', help='List all test runs')

    args = parser.parse_args()

    try:
        db = get_db()

        if args.list:
            list_test_runs(db)
            sys.exit(0)
        elif args.run_id:
            deleted = cleanup_by_run_id(db, args.run_id)
        elif args.all_tests:
            deleted = cleanup_all_tests(db)
        elif args.older_than:
            deleted = cleanup_older_than(db, args.older_than)

        if deleted == 0:
            print("⚠️  No test data found to delete")
            sys.exit(0)
        else:
            print(f"✅ Cleanup complete!")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n⚠️  Cleanup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()


