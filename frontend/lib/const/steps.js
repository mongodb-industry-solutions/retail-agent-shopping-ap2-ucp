// Conversation flow configuration for predictable journey management

export const CHAT_STEPS = {
  // straightforward shopping journey steps
  SHOPPING_AGENT_INTRODUCTION: 'shopping-agent-introduction',
  MERCHANT_AGENT_INTRODUCTION: 'merchant-agent-introduction',
  MANDATES_CREATED: 'mandates-created',
  CART_MANDATE_SIGNED_PAYMENT_CREDENTIALS: 'cart-mandate-signed-payment-credentials',
  PAYMENT_COMPLETED: 'payment-completed',
  // hunter shopping journey steps
  FIRST_HUNTER_INTENT_CREATED: 'first-hunter-intent-created',
  HUNTER_INTENT_IMMUTABILITY: 'hunter-intent-immutability',
  HUNTER_QUESTIONS_IDEMPOTENCY: 'hunter-questions-idempotency'
};
