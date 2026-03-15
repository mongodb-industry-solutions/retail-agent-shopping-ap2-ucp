// Conversation flow configuration for predictable journey management

export const CHAT_STAGES = {
  INITIAL: 'initial',
  PROVIDE_INTENT_DETAILS: 'provide_intent_details',
  ASK_REFUNDABLE: 'ask_refundable',
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
    'coffee_maker': CHAT_STAGES.ASK_REFUNDABLE,
    'headphones': CHAT_STAGES.ASK_REFUNDABLE,
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
    'coffee_maker': CHAT_STAGES.SHOW_PRODUCTS,
    'headphones': CHAT_STAGES.SHOW_PRODUCTS,
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
  [CHAT_STAGES.INITIAL]: [
    { id: 'coffee_maker', text: 'I want a coffee maker' },
    { id: 'headphones', text: 'Looking for headphones' }
  ],
  
  [CHAT_STAGES.PROVIDE_INTENT_DETAILS]: [
    { id: 'xx', text: 'xxx' },
    { id: 'xx', text: 'xxx' },
    { id: 'xx', text: 'xxx' }
  ],
  
  [CHAT_STAGES.ASK_REFUNDABLE]: [
    { id: 'yes_refundable', text: 'Yes, refundable please' },
    { id: 'no_refundable', text: 'No, that\'s fine' },
    { id: 'tell_me_more', text: 'Tell me more about refund policy' }
  ],
  
  [CHAT_STAGES.SHOW_PRODUCTS]: [
    { id: 'select_product_1', text: 'This one looks good' },
    { id: 'see_more_products', text: 'Show me more options' },
    { id: 'compare_features', text: 'Compare features' }
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
export const getChatOptions = (stage) => {
  return STAGE_OPTIONS[stage] || STAGE_OPTIONS[CHAT_STAGES.GENERAL];
};

// Get next stage based on journey type and selected option ID
export const getNextStage = (journeyType, selectedOptionId) => {
  const flow = CONVERSATION_FLOWS[journeyType];
  return flow ? flow[selectedOptionId] || CHAT_STAGES.GENERAL : CHAT_STAGES.GENERAL;
};

// Initial conversation starter
export const INITIAL_USER_MESSAGE = "Hello, I'd like to start shopping";