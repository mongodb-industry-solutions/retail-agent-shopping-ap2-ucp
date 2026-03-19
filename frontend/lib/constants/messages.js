import { CHAT_STAGES } from "../chatOptions";

// Message type constants
export const USER_ROLE = 'user';
export const AGENT_ROLE = 'agent';

// Bubble details configuration: content displayed at bottom of message bubbles
const BUBBLE_DETAILS_CONFIG = {
  user: {
    [CHAT_STAGES.INITIAL]: {
      text: "Starting your shopping journey",
      tags: ["user-intent", "session-start"]
    },
    [CHAT_STAGES.ASK_INTENT]: {
      text: "Sharing shopping intent", 
      tags: ["user-intent", "product-interest"]
    },
    [CHAT_STAGES.CONFIRM_INTENT]: {
      text: "Confirm intent.",
      tags: ["user-confirmation", "mandate-starter"]
    },
    [CHAT_STAGES.SHOW_PRODUCTS]: {
      text: "Making product selection",
      tags: ["user-selection", "product-choice"]
    },
    [CHAT_STAGES.ASK_USER_CREDENTIALS]: {
      text: "Specifying address",
      tags: ["user-credentials", "payment-preparation"]
    },
    [CHAT_STAGES.USER_CREDENTIALS_WALLET_1]: {
      text: "Selecting digital wallet",
      tags: ["user-wallet", "payment-method"]
    },
    [CHAT_STAGES.USER_CREDENTIALS_WALLET_2]: {
      text: "Authorizing wallet access",
      tags: ["user-authorization", "wallet-permission"]
    },
    [CHAT_STAGES.USER_CREDENTIALS_MANUAL_1]: {
      text: "Providing address details",
      tags: ["user-address", "manual-entry"]
    },
    [CHAT_STAGES.USER_CREDENTIALS_MANUAL_2]: {
      text: "Providing email information",
      tags: ["user-email", "contact-info"]
    },
    [CHAT_STAGES.ASK_PAYMENT_METHOD]: {
      text: "Choosing payment method", 
      tags: ["user-payment", "checkout"]
    },
    [CHAT_STAGES.CONFIRM_ORDER]: {
      text: "Order confirmation decision",
      tags: ["user-confirmation", "final-step"]
    },
    [CHAT_STAGES.VERIFICATION_CODE]: {
      text: "Entering verification code",
      tags: ["user-verification", "security-check"]
    },
    [CHAT_STAGES.ORDER_COMPLETED]: {
      text: "Order completion acknowledgment",
      tags: ["user-completion", "order-finished"]
    },
    [CHAT_STAGES.GENERAL]: {
      text: "General inquiry",
      tags: ["user-question", "general"]
    }
  },
  agent: {
    [CHAT_STAGES.ASK_INTENT]: {
      text: "AI gathering shopping preferences",
      tags: ["ai-inquiry", "intent-collection"]
    },
    [CHAT_STAGES.CONFIRM_INTENT]: {
      text: "Get user confirmation before creating a mandate.",
      tags: ["user-confirmation", "mandate-starter"]
    },
    [CHAT_STAGES.SHOW_PRODUCTS]: {
      text: "AI presenting product recommendations",
      tags: ["ai-recommendations", "product-catalog"]
    },
    [CHAT_STAGES.ASK_USER_CREDENTIALS]: {
      text: "Providing credentials for purchase",
      tags: ["user-credentials", "payment-preparation"]
    },
    [CHAT_STAGES.USER_CREDENTIALS_WALLET_1]: {
      text: "AI presenting wallet options",
      tags: ["ai-wallet-options", "payment-methods"]
    },
    [CHAT_STAGES.USER_CREDENTIALS_WALLET_2]: {
      text: "AI requesting wallet authorization",
      tags: ["ai-authorization", "wallet-permission"]
    },
    [CHAT_STAGES.USER_CREDENTIALS_MANUAL_1]: {
      text: "AI collecting address information",
      tags: ["ai-address-collection", "manual-entry"]
    },
    [CHAT_STAGES.USER_CREDENTIALS_MANUAL_2]: {
      text: "AI requesting email details",
      tags: ["ai-email-collection", "contact-info"]
    },
    [CHAT_STAGES.ASK_PAYMENT_METHOD]: {
      text: "AI processing payment options",
      tags: ["ai-payment", "checkout-flow"]
    },
    [CHAT_STAGES.CONFIRM_ORDER]: {
      text: "AI preparing order confirmation",
      tags: ["ai-confirmation", "order-processing"]
    },
    [CHAT_STAGES.VERIFICATION_CODE]: {
      text: "AI requesting verification code",
      tags: ["ai-verification", "security-check"]
    },
    [CHAT_STAGES.ORDER_COMPLETED]: {
      text: "AI confirming successful order",
      tags: ["ai-success", "order-complete"]
    },
    [CHAT_STAGES.GENERAL]: {
      text: "AI providing general assistance",
      tags: ["ai-help", "general"]
    }
  }
};

// Behind the scenes configuration: content for sidebar when message is clicked
const BEHIND_THE_SCENES_CONFIG = {
  user: {
    [CHAT_STAGES.INITIAL]: {
      title: "User Session Initialization"
    },
    [CHAT_STAGES.ASK_INTENT]: {
      title: "User Intent Declaration"
    },
    [CHAT_STAGES.CONFIRM_INTENT]: {
      title: "User Intent Confirmation"
    },
    [CHAT_STAGES.SHOW_PRODUCTS]: {
      title: "User Product Selection Process"
    },
    [CHAT_STAGES.ASK_USER_CREDENTIALS]: {
      title: "User Credentials Input Process"
    },
    [CHAT_STAGES.USER_CREDENTIALS_WALLET_1]: {
      title: "User Wallet Selection"
    },
    [CHAT_STAGES.USER_CREDENTIALS_WALLET_2]: {
      title: "User Wallet Authorization"
    },
    [CHAT_STAGES.USER_CREDENTIALS_MANUAL_1]: {
      title: "User Address Information Entry"
    },
    [CHAT_STAGES.USER_CREDENTIALS_MANUAL_2]: {
      title: "User Email Information Entry"
    },
    [CHAT_STAGES.ASK_PAYMENT_METHOD]: {
      title: "User Payment Method Choice"
    },
    [CHAT_STAGES.CONFIRM_ORDER]: {
      title: "User Order Confirmation Action"
    },
    [CHAT_STAGES.VERIFICATION_CODE]: {
      title: "User Verification Code Entry"
    },
    [CHAT_STAGES.ORDER_COMPLETED]: {
      title: "User Order Completion Acknowledgment"
    },
    [CHAT_STAGES.GENERAL]: {
      title: "User General Interaction"
    }
  },
  agent: {
    [CHAT_STAGES.INITIAL]: {
      title: "Agent Welcome & Options Presentation"
    },
    [CHAT_STAGES.ASK_INTENT]: {
      title: "Agent Intent Collection Workflow"
    },
    [CHAT_STAGES.CONFIRM_INTENT]: {
      title: "Agent Intent Confirmation Process"
    },
    [CHAT_STAGES.SHOW_PRODUCTS]: {
      title: "Agent Product Recommendation Engine"
    },
    [CHAT_STAGES.ASK_USER_CREDENTIALS]: {
      title: "Agent Credentials Collection System"
    },
    [CHAT_STAGES.USER_CREDENTIALS_WALLET_1]: {
      title: "Agent Wallet Options Presentation"
    },
    [CHAT_STAGES.USER_CREDENTIALS_WALLET_2]: {
      title: "Agent Wallet Authorization Handler"
    },
    [CHAT_STAGES.USER_CREDENTIALS_MANUAL_1]: {
      title: "Agent Address Collection Interface"
    },
    [CHAT_STAGES.USER_CREDENTIALS_MANUAL_2]: {
      title: "Agent Email Collection Interface"
    },
    [CHAT_STAGES.ASK_PAYMENT_METHOD]: {
      title: "Agent Payment Processing Setup"
    },
    [CHAT_STAGES.CONFIRM_ORDER]: {
      title: "Agent Order Validation & Confirmation"
    },
    [CHAT_STAGES.VERIFICATION_CODE]: {
      title: "Agent Verification Code Processing"
    },
    [CHAT_STAGES.ORDER_COMPLETED]: {
      title: "Agent Order Completion Handler"
    },
    [CHAT_STAGES.GENERAL]: {
      title: "Agent General Assistant Mode"
    }
  }
};

// Get bubble details based on message type and stage
export const getBubbleDetails = (type, stage) => {
  const defaultDetails = { text: "", tags: [] };
  return BUBBLE_DETAILS_CONFIG[type]?.[stage] || defaultDetails;
};

// Get behind the scenes info based on message type and stage  
export const getBehindTheScenes = (type, stage) => {
  const defaultBehindScenes = { title: "Message Processing" };
  return BEHIND_THE_SCENES_CONFIG[type]?.[stage] || defaultBehindScenes;
};