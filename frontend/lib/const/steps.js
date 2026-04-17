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
  HUNTER_QUESTIONS_IDEMPOTENCY: 'hunter-questions-idempotency',
  // disputing journey steps
  MEET_AUDITOR_AGENT: 'meet-auditor-agent',
  SIGNATURE_FLOW_AND_AUDIT_TRACE: 'signature-flow-and-audit-trace',
  WHY_SIGNATURES_MATTER: 'why-signatures-matter',
  IMMUTABILITY_AND_RBAC_PROTECTIONS: 'immutability-and-rbac-protections',
  WHY_MONGODB_FOR_MANDATE_LEDGER: 'why-mongodb-for-mandate-ledger'
};
