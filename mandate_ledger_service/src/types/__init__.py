# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
AP2 Protocol Type Definitions

DUPLICATION NOTE:
These types are temporarily duplicated from the parent AP2 project
(src/ap2/types/) to make the Mandate Ledger Service standalone.

Source: /Users/sakshi.garg/AP2-test/AP2/src/ap2/types/
Duplicated: 2025-11-14
Reason: Enable standalone deployment for POC

Future Plan:
Once this service is production-ready, these types should be:
1. Published as 'ap2-types' PyPI package by Google
2. OR: Used directly from parent project via editable install
3. Then: Remove duplication and use versioned dependency

See DUPLICATION_NOTE.md for full context.
"""

# Re-export all AP2 types for convenient imports
from src.types.ap2_contact import ContactAddress, CONTACT_ADDRESS_DATA_KEY
from src.types.ap2_payment_request import (
    PaymentCurrencyAmount,
    PaymentItem,
    PaymentShippingOption,
    PaymentOptions,
    PaymentMethodData,
    PaymentDetailsModifier,
    PaymentDetailsInit,
    PaymentRequest,
    PaymentResponse,
    PAYMENT_METHOD_DATA_DATA_KEY,
)
from src.types.ap2_mandate import (
    IntentMandate,
    CartContents,
    CartMandate,
    PaymentMandateContents,
    PaymentMandate,
    CART_MANDATE_DATA_KEY,
    INTENT_MANDATE_DATA_KEY,
    PAYMENT_MANDATE_DATA_KEY,
)

__all__ = [
    # Contact types
    "ContactAddress",
    "CONTACT_ADDRESS_DATA_KEY",
    # Payment Request types
    "PaymentCurrencyAmount",
    "PaymentItem",
    "PaymentShippingOption",
    "PaymentOptions",
    "PaymentMethodData",
    "PaymentDetailsModifier",
    "PaymentDetailsInit",
    "PaymentRequest",
    "PaymentResponse",
    "PAYMENT_METHOD_DATA_DATA_KEY",
    # Mandate types
    "IntentMandate",
    "CartContents",
    "CartMandate",
    "PaymentMandateContents",
    "PaymentMandate",
    "CART_MANDATE_DATA_KEY",
    "INTENT_MANDATE_DATA_KEY",
    "PAYMENT_MANDATE_DATA_KEY",
]




