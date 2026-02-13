#!/bin/bash
#
# Cleanup Wrapper Script
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_usage() {
    cat <<EOF
Usage: cleanup.sh [OPTIONS]

Cleanup test data from MongoDB.

Options:
    --run-id ID       Clean specific test run
    --all             Clean all test data
    --old [DAYS]      Clean data older than N days (default: 7)
    --list            List all test runs
    --help            Show this help

Examples:
    ./cleanup.sh --all
    ./cleanup.sh --run-id test_1700000000_12345
    ./cleanup.sh --old 7
    ./cleanup.sh --list

EOF
}

if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

case "$1" in
    --run-id)
        if [ -z "${2:-}" ]; then
            echo "${RED}Error: --run-id requires an argument${NC}"
            exit 1
        fi
        python3 "$TEST_DIR/cleanup_test_data.py" --run-id "$2"
        ;;
    --all)
        echo "${YELLOW}⚠️  This will delete ALL test data. Continue? (y/N)${NC}"
        read -r confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            python3 "$TEST_DIR/cleanup_test_data.py" --all-tests
        else
            echo "Cancelled"
        fi
        ;;
    --old)
        days=${2:-7}
        python3 "$TEST_DIR/cleanup_test_data.py" --older-than "$days"
        ;;
    --list)
        python3 "$TEST_DIR/cleanup_test_data.py" --list
        ;;
    --help|-h)
        show_usage
        ;;
    *)
        echo "${RED}Unknown option: $1${NC}"
        show_usage
        exit 1
        ;;
esac


