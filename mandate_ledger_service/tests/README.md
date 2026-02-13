# API Test Suite

Comprehensive test suite for the Mandate Ledger Service API endpoints.

## 📁 Structure

```
tests/
├── api/
│   ├── test_auth.sh          # Auth endpoint tests (6 tests)
│   └── test_mandates.sh       # Mandate CRUD tests (8 tests)
├── utils/
│   ├── test_helpers.sh        # Shared test utilities
│   └── assertions.sh          # Test assertion functions
├── fixtures/
│   ├── test_config.sh         # Test configuration
│   ├── intent_mandate.json    # Intent test data
│   ├── cart_mandate.json      # Cart test data
│   └── payment_mandate.json   # Payment test data
├── cleanup_test_data.py       # Cleanup script
├── run_all_tests.sh           # Test runner
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Setup

Make sure your API server is running:

```bash
cd /Users/sakshi.garg/AP2-test/AP2/mandate_ledger_service
.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Configure

The tests use your bootstrap admin key by default. Alternatively, set an API key:

```bash
export API_KEY="your_api_key_here"
```

### 3. Run Tests

Run all tests:

```bash
cd tests
chmod +x run_all_tests.sh api/*.sh
./run_all_tests.sh
```

Run individual test suites:

```bash
cd tests
./api/test_auth.sh
./api/test_mandates.sh
```

## 🧹 Cleanup Test Data

Test data is automatically cleaned up after each test run. All test entities are prefixed with `test_<timestamp>_` and marked with `metadata.is_test: true`.

### Automatic Cleanup

Tests automatically clean up their data when they finish (using `trap EXIT`).

### Manual Cleanup

Clean up specific test run:
```bash
python tests/cleanup_test_data.py --run-id test_1700000000_12345
```

Clean up all test data:
```bash
python tests/cleanup_test_data.py --all-tests
```

Clean up old test data (7+ days):
```bash
python tests/cleanup_test_data.py --older-than 7
```

List all test runs:
```bash
python tests/cleanup_test_data.py --list
```

### Skip Cleanup

To keep test data for debugging:

```bash
SKIP_CLEANUP=true ./api/test_auth.sh
```

## 📊 Test Output

Tests produce colored output with clear pass/fail indicators:

```
================================================
🔐 Testing Auth Endpoints
   Test Run ID: test_1700000000_12345
   Base URL: http://localhost:8000
================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Test 1: Create API Key
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PASS: Create API Key

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Test 2: List API Keys
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PASS: List API Keys

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Passed:  6
❌ Failed:  0
⊘ Skipped: 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 6 tests

🧹 Cleaning up test data for run: test_1700000000_12345
```

## 🧪 Test Suites

### Auth Tests (`test_auth.sh`)

Tests API key management endpoints:

1. ✅ Create API key (success)
2. ✅ List API keys
3. ✅ Get API key details
4. ✅ Revoke API key
5. ✅ Create API key (invalid request - should fail)
6. ✅ Get non-existent key (should fail)

### Mandate Tests (`test_mandates.sh`)

Tests mandate CRUD operations:

1. ✅ Create Intent mandate
2. ✅ Get mandate
3. ✅ Update mandate (Intent → Cart)
4. ✅ Get mandate history
5. ✅ Search mandates
6. ✅ Create Cart mandate (direct)
7. ✅ Create Payment mandate (direct)
8. ✅ Get non-existent mandate (should fail)

## 🛠️ Configuration

### Environment Variables

- `BASE_URL` - API base URL (default: `http://localhost:8000`)
- `API_KEY` - API key for authentication
- `MONGODB_URI` - MongoDB connection string (for cleanup)
- `MONGODB_DATABASE` - Database name (default: `mandate_ledger`)
- `SKIP_CLEANUP` - Set to `true` to keep test data

### Test Configuration File

Edit `fixtures/test_config.sh` to change defaults.

## 📝 Writing New Tests

### Test Template

```bash
#!/bin/bash
set -euo pipefail

# Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$SCRIPT_DIR")"

source "$TEST_DIR/utils/test_helpers.sh"
source "$TEST_DIR/utils/assertions.sh"
source "$TEST_DIR/fixtures/test_config.sh"

export TEST_SUITE="test_my_feature.sh"

# Test function
test_my_feature() {
    print_test_header "Test 1: My Feature"

    local response=$(api_request GET "/api/v1/my-endpoint")

    if assert_status 200; then
        print_result "My Feature" true
    else
        print_result "My Feature" false "Status: $LAST_STATUS"
    fi
}

# Run tests
test_my_feature

# Summary
print_summary
exit $?
```

### Using Test Helpers

```bash
# Generate unique test IDs
entity_id=$(generate_test_id "mandate")
agent_id=$(generate_test_agent_id "shopper")

# Make API requests
response=$(api_request POST "/api/v1/endpoint" "$json_data")
response=$(api_request GET "/api/v1/endpoint")

# Access last response
echo "$LAST_RESPONSE"
echo "$LAST_STATUS"

# Assertions
assert_status 200
assert_json_equals ".field" "expected_value"
assert_json_exists ".field"
assert_valid_uuid "$uuid_value"
```

## 🔍 Debugging

### Verbose Mode

```bash
VERBOSE=true ./api/test_auth.sh
```

### Keep Test Data

```bash
SKIP_CLEANUP=true ./api/test_auth.sh
```

### Check MongoDB

```javascript
// Find all test data
db.mandate_ledger.find({"metadata.is_test": true})

// Count test mandates
db.mandate_ledger.countDocuments({"metadata.is_test": true})

// List test run IDs
db.mandate_ledger.distinct("metadata.test_run_id", {"metadata.is_test": true})
```

## 🎯 CI/CD Integration

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mongodb:
        image: mongo:7.0
        ports:
          - 27017:27017

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Start API server
        run: |
          uvicorn src.main:app &
          sleep 5

      - name: Run tests
        run: |
          cd tests
          chmod +x run_all_tests.sh api/*.sh
          ./run_all_tests.sh
```

## 📦 Dependencies

- `bash` 4.0+
- `curl`
- `jq` - JSON processor
- `python3` - For cleanup script
- `pymongo` - Python MongoDB driver

Install Python dependencies:

```bash
pip install pymongo
```

## 🤝 Contributing

When adding new tests:

1. Follow the existing test structure
2. Use test helpers and assertions
3. Add test metadata to all created entities
4. Document your tests in this README
5. Ensure cleanup works correctly

## 📄 License

Copyright 2025 Google LLC
Licensed under the Apache License, Version 2.0


