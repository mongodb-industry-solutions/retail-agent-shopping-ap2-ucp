import { CHAT_STEPS } from "./steps";

// Message type constants for dynamic workflow management
export const USER_ROLE = "user";
export const AGENT_ROLE = "agent";
export const SYSTEM_ROLE = "system";

const BUBBLE_DETAILS_CONFIG = {
  [AGENT_ROLE]: {
    // straightforward shopping journey bubble details
    [CHAT_STEPS.SHOPPING_AGENT_INTRODUCTION]: {
      text: "Meet your shopping agent and how it securely connects across the agentic commerce landscape to find the best offers for you.",
      tags: ["Shopping Agent", "UCP", "AP2"],
    },
    [CHAT_STEPS.MERCHANT_AGENT_INTRODUCTION]: {
      text: "Discover how the Shopping Agent interacts with the Merchant Agent behind the scenes to provide the best options based on your preferences.",
      tags: ["Merchant Agent", "A2A", "AP2", "Cryptographic Mandates"],
    },
    [CHAT_STEPS.MANDATES_CREATED]: {
      text: "The Shopping Agent has already sent a signed intent mandate to the Merchant Agent, which creates a proposed Cart Mandate, securely stored in MongoDB for audit and trust.",
      tags: [
        "Intent Mandate Signed",
        "Cart Mandate Proposed",
        "Mandate Ledger Service on MongoDB",
      ],
    },
    [CHAT_STEPS.CART_MANDATE_SIGNED_PAYMENT_CREDENTIALS]: {
      text: "The Shopping Agent signs the Cart Mandate, confirmed by the user for the purchase. The transaction flow then starts by requesting payment credentials from the Credential Provider Agent.",
      tags: [
        "Cart Mandate Signed",
        "Mandate Ledger Service on MongoDB",
        "Credential Provider Agent",
      ],
    },
    [CHAT_STEPS.PAYMENT_COMPLETED]: {
      text: "Discover how the completed purchase is stored as a secure, reliable, and auditable transaction.",
      tags: ["Payment Mandate", "AP2", "Mandate Ledger Service on MongoDB"],
    },
    // hunter shopping journey bubble details
    [CHAT_STEPS.FIRST_HUNTER_INTENT_CREATED]: {
      text: "The purchase intent becomes a verifiable digital contract",
      tags: ["Digital Contracts", "Authorization & Auditability", "Authenticity of Intent", "MongoDB's Flexible Document Model"],
    },
    [CHAT_STEPS.HUNTER_INTENT_IMMUTABILITY]: {
      text: "Understand how the ledger blocks updates and deletes, even if an agent retries, fails, or tries to correct a previous mandate.",
      tags: ["Immutability", "Mandate Ledger Service", "Append-Only Writes"],
    },
    [CHAT_STEPS.HUNTER_QUESTIONS_IDEMPOTENCY]: {
      text: "See how duplicate executions are prevented",
      tags: ["Idempotency", "Mandate Ledger Service"],
    },
    // dispute journey bubble details
    [CHAT_STEPS.MEET_AUDITOR_AGENT]: {
      text: "Meet the auditor agent",
      tags: ["Read-Only Access", "Audit Trail"],
    },
    [CHAT_STEPS.SIGNATURE_FLOW_AND_AUDIT_TRACE]: {
      text: "See how the Auditor Agent can reconstructs the full transaction history",
      tags: ["Audit Trail", "Cryptographic Signatures", "Transaction History"],
    },
    [CHAT_STEPS.WHY_SIGNATURES_MATTER]: {
      text: "How trust is proven, not assumed: Verify authenticity and integrity",
      tags: [],
    },
    [CHAT_STEPS.IMMUTABILITY_AND_RBAC_PROTECTIONS]: {
      text: "See why attempts to change or delete signed transaction records are rejected, and how role-based permissions protect the ledger",
      tags: ["Append-Only", "Minimum Necessary Permissions", "Role Based Access Control"],
    },
    [CHAT_STEPS.WHY_MONGODB_FOR_MANDATE_LEDGER]: {
      text: "Why MongoDB is the ideal foundation for the Mandate Ledger",
      tags: ["MongoDB", "Mandate Ledger Service", "Scalability", "Reliability"],
    },
  },
  [USER_ROLE]: {},
};

// These functions will now return null since bubble details and behind the scenes
// data will come dynamically from the assistant API, but we keep them for compatibility
export const getBubbleDetails = (type, step) => {
  return BUBBLE_DETAILS_CONFIG[type]?.[step] || null;
};
