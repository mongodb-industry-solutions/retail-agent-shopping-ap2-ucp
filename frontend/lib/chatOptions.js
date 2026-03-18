// Conversation flow configuration for predictable journey management

export const CHAT_STAGES = {
  INITIAL: 'initial',
  ASK_INTENT: 'ask_intent',
  CONFIRM_INTENT: 'confirm_intent',
  SHOW_PRODUCTS: 'show_products', 
  ASK_PAYMENT_METHOD: 'ask_payment_method',
  CONFIRM_ORDER: 'confirm_order',
  ORDER_COMPLETE: 'order_complete',
  ASK_DISPUTE_REASON: 'ask_dispute_reason',
  REQUEST_EVIDENCE: 'request_evidence',
  SHOW_RESOLUTION: 'show_resolution',
  DISPUTE_CLOSED: 'dispute_closed',
  ESCALATE_DISPUTE: 'escalate_dispute',
  GENERAL: 'general'
};

// Direct mapping: journey + option ID → next stage
export const CONVERSATION_FLOWS = {
  straightforward: {
    'coffee_maker': CHAT_STAGES.CONFIRM_INTENT,
    'headphones': CHAT_STAGES.CONFIRM_INTENT,
    'confirm_intent': CHAT_STAGES.SHOW_PRODUCTS,
    'more_details': CHAT_STAGES.PROVIDE_INTENT_DETAILS,
    'price_range': CHAT_STAGES.ASK_REFUNDABLE,
    'yes_refundable': CHAT_STAGES.SHOW_PRODUCTS,
    'no_refundable': CHAT_STAGES.SHOW_PRODUCTS,
    'select_product_1': CHAT_STAGES.ASK_PAYMENT_METHOD,
    'see_more_products': CHAT_STAGES.SHOW_PRODUCTS,
    'credit_card': CHAT_STAGES.CONFIRM_ORDER,
    'paypal': CHAT_STAGES.CONFIRM_ORDER,
    'confirm_purchase': CHAT_STAGES.ORDER_COMPLETE,
    'modify_order': CHAT_STAGES.SHOW_PRODUCTS
  },
  disputing: {
    'dispute_charge': CHAT_STAGES.ASK_DISPUTE_REASON,
    'wrong_amount': CHAT_STAGES.REQUEST_EVIDENCE, 
    'defective_product': CHAT_STAGES.REQUEST_EVIDENCE,
    'unauthorized_charge': CHAT_STAGES.REQUEST_EVIDENCE,
    'submit_evidence': CHAT_STAGES.SHOW_RESOLUTION,
    'need_help_evidence': CHAT_STAGES.REQUEST_EVIDENCE,
    'accept_resolution': CHAT_STAGES.DISPUTE_CLOSED,
    'reject_resolution': CHAT_STAGES.ESCALATE_DISPUTE,
    'escalate_now': CHAT_STAGES.DISPUTE_CLOSED
  },
  
  hunter: {
    'coffee_maker': CHAT_STAGES.PROVIDE_INTENT_DETAILS,
    'headphones': CHAT_STAGES.PROVIDE_INTENT_DETAILS,
    'compare_features': CHAT_STAGES.SHOW_PRODUCTS,
    'check_reviews': CHAT_STAGES.ASK_PAYMENT_METHOD,
    'select_product_1': CHAT_STAGES.ASK_PAYMENT_METHOD,
    'credit_card': CHAT_STAGES.CONFIRM_ORDER,
    'confirm_purchase': CHAT_STAGES.ORDER_COMPLETE
  }
};

// Stage-specific options that appear after agent responses
// Important: keep option IDs in sync with CONVERSATION_FLOWS
export const STAGE_OPTIONS = {
  [CHAT_STAGES.ASK_INTENT]: [
    { id: 'coffee_maker', text: 'I want a coffee maker, of type of french press. I do not have any prefered merchant. Also, I want it to be refundable. Show me some options.' },
    { id: 'headphones', text: 'Looking for headphones for gaming and noice cancelling. They dont need to be refundable, but i want the merchant Amazon. Show me some options.' },
  ],

  [CHAT_STAGES.CONFIRM_INTENT]: [
    { id: 'confirm_intent', text: 'Yes, I confirm' },
  ],
  
  [CHAT_STAGES.SHOW_PRODUCTS]: [
    { id: 'select_product_1', text: 'Option 1 looks good' },
    { id: 'select_product_2', text: 'I want option 2' },
    { id: 'select_product_3', text: 'Option 3 please' }
  ],
  
  [CHAT_STAGES.ASK_PAYMENT_METHOD]: [
    { id: 'credit_card', text: 'Credit Card' },
    { id: 'paypal', text: 'PayPal' },
    { id: 'apple_pay', text: 'Apple Pay' }
  ],
  
  [CHAT_STAGES.CONFIRM_ORDER]: [
    { id: 'confirm_purchase', text: 'Yes, confirm my order' },
    { id: 'modify_order', text: 'I want to modify something' },
    { id: 'cancel_order', text: 'Cancel this order' }
  ],
  
  [CHAT_STAGES.ASK_DISPUTE_REASON]: [
    { id: 'wrong_amount', text: 'Wrong amount charged' },
    { id: 'defective_product', text: 'Product was defective' },
    { id: 'unauthorized_charge', text: 'Unauthorized charge' }
  ],
  
  [CHAT_STAGES.REQUEST_EVIDENCE]: [
    { id: 'submit_evidence', text: 'I have the evidence ready' },
    { id: 'need_help_evidence', text: 'I need help gathering evidence' },
    { id: 'upload_receipt', text: 'Upload receipt/photos' }
  ],
  
  [CHAT_STAGES.SHOW_RESOLUTION]: [
    { id: 'accept_resolution', text: 'Accept this resolution' },
    { id: 'reject_resolution', text: 'I disagree with this' },
    { id: 'need_clarification', text: 'I need more details' }
  ],
  
  [CHAT_STAGES.GENERAL]: [
    { id: 'more_info', text: 'Tell me more about this' },
    { id: 'different_options', text: 'Show me something different' },
    { id: 'need_help', text: 'I need help deciding' }
  ]
};

// Get options for a specific stage
export const getChatOptions = (stage, context = null) => {
  const stageOptions = STAGE_OPTIONS[stage];
  
  // Handle nested context-dependent stages
  if (typeof stageOptions === 'object' && !Array.isArray(stageOptions)) {
    // If context provided and exists in nested options, return those
    if (context && stageOptions[context]) {
      return stageOptions[context];
    }
    // Otherwise return default options or first available
    return stageOptions.default || Object.values(stageOptions)[0] || STAGE_OPTIONS[CHAT_STAGES.GENERAL];
  }
  
  // Handle regular array-based stages
  return stageOptions || STAGE_OPTIONS[CHAT_STAGES.GENERAL];
};

// Get next stage based on journey type and selected option ID
export const getNextStage = (journeyType, selectedOptionId) => {
  const flow = CONVERSATION_FLOWS[journeyType];
  return flow ? flow[selectedOptionId] || CHAT_STAGES.GENERAL : CHAT_STAGES.GENERAL;
};

// Initial conversation starter
export const INITIAL_USER_MESSAGE = "Hello, I'd like to start shopping";

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
    [CHAT_STAGES.PROVIDE_INTENT_DETAILS]: {
      text: "Providing more details about your needs",
      tags: ["user-input", "clarification"]
    },
    [CHAT_STAGES.ASK_REFUNDABLE]: {
      text: "Sharing refund preferences",
      tags: ["user-preference", "refund-policy"]
    },
    [CHAT_STAGES.SHOW_PRODUCTS]: {
      text: "Making product selection",
      tags: ["user-selection", "product-choice"]
    },
    [CHAT_STAGES.ASK_PAYMENT_METHOD]: {
      text: "Choosing payment method", 
      tags: ["user-payment", "checkout"]
    },
    [CHAT_STAGES.CONFIRM_ORDER]: {
      text: "Order confirmation decision",
      tags: ["user-confirmation", "final-step"]
    },
    [CHAT_STAGES.ASK_DISPUTE_REASON]: {
      text: "Explaining dispute reason",
      tags: ["user-dispute", "issue-reporting"]
    },
    [CHAT_STAGES.REQUEST_EVIDENCE]: {
      text: "Providing evidence details",
      tags: ["user-evidence", "dispute-support"]
    },
    [CHAT_STAGES.SHOW_RESOLUTION]: {
      text: "Responding to resolution",
      tags: ["user-response", "resolution-feedback"]
    },
    [CHAT_STAGES.GENERAL]: {
      text: "General inquiry",
      tags: ["user-question", "general"]
    }
  },
  agent: {
    [CHAT_STAGES.INITIAL]: {
      text: "AI Assistant providing shopping options",
      tags: ["ai-response", "options-presented"]
    },
    [CHAT_STAGES.ASK_INTENT]: {
      text: "AI gathering shopping preferences",
      tags: ["ai-inquiry", "intent-collection"]
    },
    [CHAT_STAGES.PROVIDE_INTENT_DETAILS]: {
      text: "AI gathering more information",
      tags: ["ai-clarification", "data-collection"]
    },
    [CHAT_STAGES.ASK_REFUNDABLE]: {
      text: "AI explaining refund policies",
      tags: ["ai-policy", "refund-info"]
    },
    [CHAT_STAGES.SHOW_PRODUCTS]: {
      text: "AI presenting product recommendations",
      tags: ["ai-recommendations", "product-catalog"]
    },
    [CHAT_STAGES.ASK_PAYMENT_METHOD]: {
      text: "AI processing payment options",
      tags: ["ai-payment", "checkout-flow"]
    },
    [CHAT_STAGES.CONFIRM_ORDER]: {
      text: "AI preparing order confirmation",
      tags: ["ai-confirmation", "order-processing"]
    },
    [CHAT_STAGES.ORDER_COMPLETE]: {
      text: "AI confirming successful order",
      tags: ["ai-success", "order-complete"]
    },
    [CHAT_STAGES.ASK_DISPUTE_REASON]: {
      text: "AI collecting dispute information",
      tags: ["ai-dispute", "issue-resolution"]
    },
    [CHAT_STAGES.REQUEST_EVIDENCE]: {
      text: "AI guiding evidence submission",
      tags: ["ai-guidance", "evidence-help"]
    },
    [CHAT_STAGES.SHOW_RESOLUTION]: {
      text: "AI presenting resolution options",
      tags: ["ai-resolution", "dispute-outcome"]
    },
    [CHAT_STAGES.DISPUTE_CLOSED]: {
      text: "AI confirming dispute closure",
      tags: ["ai-closure", "dispute-resolved"]
    },
    [CHAT_STAGES.ESCALATE_DISPUTE]: {
      text: "AI escalating to human support",
      tags: ["ai-escalation", "human-handoff"]
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
    [CHAT_STAGES.PROVIDE_INTENT_DETAILS]: {
      title: "User Intent Clarification"
    },
    [CHAT_STAGES.ASK_REFUNDABLE]: {
      title: "User Refund Preference Input"
    },
    [CHAT_STAGES.SHOW_PRODUCTS]: {
      title: "User Product Selection Process"
    },
    [CHAT_STAGES.ASK_PAYMENT_METHOD]: {
      title: "User Payment Method Choice"
    },
    [CHAT_STAGES.CONFIRM_ORDER]: {
      title: "User Order Confirmation Action"
    },
    [CHAT_STAGES.ASK_DISPUTE_REASON]: {
      title: "User Dispute Reason Submission"
    },
    [CHAT_STAGES.REQUEST_EVIDENCE]: {
      title: "User Evidence Preparation"
    },
    [CHAT_STAGES.SHOW_RESOLUTION]: {
      title: "User Resolution Response"
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
    [CHAT_STAGES.PROVIDE_INTENT_DETAILS]: {
      title: "Agent Information Gathering"
    },
    [CHAT_STAGES.ASK_REFUNDABLE]: {
      title: "Agent Refund Policy Explanation"
    },
    [CHAT_STAGES.SHOW_PRODUCTS]: {
      title: "Agent Product Recommendation Engine"
    },
    [CHAT_STAGES.ASK_PAYMENT_METHOD]: {
      title: "Agent Payment Processing Setup"
    },
    [CHAT_STAGES.CONFIRM_ORDER]: {
      title: "Agent Order Validation & Confirmation"
    },
    [CHAT_STAGES.ORDER_COMPLETE]: {
      title: "Agent Order Completion Processing"
    },
    [CHAT_STAGES.ASK_DISPUTE_REASON]: {
      title: "Agent Dispute Analysis & Classification"
    },
    [CHAT_STAGES.REQUEST_EVIDENCE]: {
      title: "Agent Evidence Collection Workflow"
    },
    [CHAT_STAGES.SHOW_RESOLUTION]: {
      title: "Agent Resolution Algorithm Execution"
    },
    [CHAT_STAGES.DISPUTE_CLOSED]: {
      title: "Agent Case Closure Processing"
    },
    [CHAT_STAGES.ESCALATE_DISPUTE]: {
      title: "Agent Human Escalation Trigger"
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