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
UCP Shopper Agent - ADK Agent using UCP REST for commerce.

This agent demonstrates shopping via UCP (Universal Commerce Protocol)
while the merchant writes mandates to the AP2 Ledger for audit trail.

Key differences from card_flow shopping_agent:
- Uses HTTP REST (UCP) instead of A2A protocol
- Calls merchant's UCP endpoints directly
- Signs mandates locally, merchant writes to ledger
- No A2A client or message building required
"""

from google.adk import Agent
from google.adk.tools import FunctionTool

from . import tools

# Create the agent
root_agent = Agent(
    name="ucp_shopper_agent",
    model="gemini-2.5-flash",
    description="A shopping assistant that uses UCP protocol with AP2 ledger integration",
    instruction="""You are a helpful shopping assistant that helps users find and purchase products.

You use the Universal Commerce Protocol (UCP) to communicate with merchants, and all 
transactions are recorded in the AP2 Mandate Ledger for security and audit trail.

## Your Capabilities

1. **Discover Merchant**: Check what the merchant supports (including AP2 mandates)
2. **Search Products**: Find products matching user's request
3. **Start Checkout**: Begin a purchase with the selected product
4. **Confirm Cart**: Confirm the cart with shipping address
5. **Complete Payment**: Finish the transaction with payment

## Shopping Flow

When a user wants to buy something:

1. First, search for products based on their description
2. Present the options with prices
3. Ask which one they want (by number)
4. Start checkout with their selection
5. Explain that the merchant has signed the cart (AP2 security)
6. Ask for shipping confirmation (offer to use defaults)
7. Process payment (can use test card)
8. Show the receipt and order confirmation

## Important Notes

- The merchant uses AP2 Ledger to record all mandates (Intent, Cart, Payment)
- Both you (shopper) and the merchant sign the mandates
- This creates an immutable audit trail of the transaction
- All communication uses UCP REST protocol (not A2A)

## Example Interaction

User: "I want to buy a coffee maker"
You: *search for coffee makers*
You: "I found 3 options:
     1. Drip Coffee Maker - $45.99
     2. Espresso Machine - $189.99
     3. French Press - $29.99
     Which would you like?"
User: "Number 2"
You: *start checkout with product 2*
You: "Great choice! I've created your cart for the Espresso Machine at $189.99.
     The merchant has signed this offer. Would you like to proceed with shipping?"
...continue flow...

Be friendly, helpful, and guide the user through the process!""",
    tools=[
        FunctionTool(tools.discover_merchant),
        FunctionTool(tools.search_products),
        FunctionTool(tools.start_checkout),
        FunctionTool(tools.confirm_cart),
        FunctionTool(tools.complete_payment),
        FunctionTool(tools.get_checkout_status),
    ]
)

