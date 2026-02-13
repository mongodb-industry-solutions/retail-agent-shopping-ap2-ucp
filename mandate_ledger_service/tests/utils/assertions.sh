#!/bin/bash
#
# Assertions - Test assertion functions
#

# Assert HTTP status code
assert_status() {
    local expected=$1
    local actual=${LAST_STATUS:-0}

    if [ "$actual" -eq "$expected" ]; then
        return 0
    else
        echo "Expected status $expected, got $actual"
        if [ -n "${LAST_RESPONSE:-}" ]; then
            echo "Response: $LAST_RESPONSE"
        fi
        return 1
    fi
}

# Assert JSON field equals value
assert_json_equals() {
    local field=$1
    local expected=$2
    local json=${3:-$LAST_RESPONSE}

    local actual=$(echo "$json" | jq -r "$field")

    if [ "$actual" = "$expected" ]; then
        return 0
    else
        echo "Field '$field': expected '$expected', got '$actual'"
        return 1
    fi
}

# Assert JSON field exists
assert_json_exists() {
    local field=$1
    local json=${2:-$LAST_RESPONSE}

    local value=$(echo "$json" | jq -r "$field")

    if [ "$value" != "null" ] && [ -n "$value" ]; then
        return 0
    else
        echo "Field '$field' does not exist or is null"
        return 1
    fi
}

# Assert JSON field is not empty
assert_json_not_empty() {
    local field=$1
    local json=${2:-$LAST_RESPONSE}

    local value=$(echo "$json" | jq -r "$field")

    if [ "$value" != "null" ] && [ -n "$value" ] && [ "$value" != "" ]; then
        return 0
    else
        echo "Field '$field' is empty or null"
        return 1
    fi
}

# Assert string contains substring
assert_contains() {
    local haystack=$1
    local needle=$2

    if [[ "$haystack" == *"$needle"* ]]; then
        return 0
    else
        echo "'$haystack' does not contain '$needle'"
        return 1
    fi
}

# Assert string equals
assert_equals() {
    local expected=$1
    local actual=$2

    if [ "$actual" = "$expected" ]; then
        return 0
    else
        echo "Expected '$expected', got '$actual'"
        return 1
    fi
}

# Assert not equals
assert_not_equals() {
    local not_expected=$1
    local actual=$2

    if [ "$actual" != "$not_expected" ]; then
        return 0
    else
        echo "Expected value to not equal '$not_expected', but it did"
        return 1
    fi
}

# Assert value is valid UUID
assert_valid_uuid() {
    local value=$1
    local uuid_regex='^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

    if [[ "$value" =~ $uuid_regex ]]; then
        return 0
    else
        echo "'$value' is not a valid UUID"
        return 1
    fi
}

# Assert value is valid ISO 8601 date
assert_valid_iso_date() {
    local value=$1
    # Basic ISO 8601 check
    if [[ "$value" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2} ]]; then
        return 0
    else
        echo "'$value' is not a valid ISO 8601 date"
        return 1
    fi
}

# Assert array length
assert_array_length() {
    local field=$1
    local expected_length=$2
    local json=${3:-$LAST_RESPONSE}

    local actual_length=$(echo "$json" | jq -r "$field | length")

    if [ "$actual_length" -eq "$expected_length" ]; then
        return 0
    else
        echo "Array '$field' length: expected $expected_length, got $actual_length"
        return 1
    fi
}

# Assert value is greater than
assert_greater_than() {
    local actual=$1
    local threshold=$2

    if [ "$actual" -gt "$threshold" ]; then
        return 0
    else
        echo "Expected $actual > $threshold"
        return 1
    fi
}

# Export functions
export -f assert_status
export -f assert_json_equals
export -f assert_json_exists
export -f assert_json_not_empty
export -f assert_contains
export -f assert_equals
export -f assert_not_equals
export -f assert_valid_uuid
export -f assert_valid_iso_date
export -f assert_array_length
export -f assert_greater_than

