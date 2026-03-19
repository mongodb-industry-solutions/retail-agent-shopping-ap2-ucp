// Conversation flow configuration for predictable journey management

export const CHAT_STAGES = {
  INITIAL: 'initial',
  ASK_INTENT: 'ask_intent',
  CONFIRM_INTENT: 'confirm_intent',
  SHOW_PRODUCTS: 'show_products', 
  ASK_USER_CREDENTIALS: 'ask_user_credentials',
  USER_CREDENTIALS_WALLET_1: 'select_wallet',
  USER_CREDENTIALS_WALLET_2: 'allow_wallet_access',
  USER_CREDENTIALS_MANUAL_1: 'provide_address',
  USER_CREDENTIALS_MANUAL_2: 'provide_email',
  ASK_PAYMENT_METHOD: 'ask_payment_method',
  CONFIRM_ORDER: 'confirm_order',
  VERIFICATION_CODE: 'verification_code',
  ORDER_COMPLETED: 'order_completed',

  GENERAL: 'general'
};

// Direct mapping: journey + option ID → next stage
export const CONVERSATION_FLOWS = {
  straightforward: {
    'coffee_maker': CHAT_STAGES.CONFIRM_INTENT,
    'headphones': CHAT_STAGES.CONFIRM_INTENT,
    'confirm_intent': CHAT_STAGES.SHOW_PRODUCTS,

    'select_product_1': CHAT_STAGES.ASK_USER_CREDENTIALS,
    'select_product_2': CHAT_STAGES.ASK_USER_CREDENTIALS,
    'select_product_3': CHAT_STAGES.ASK_USER_CREDENTIALS,

    'use_wallet': CHAT_STAGES.USER_CREDENTIALS_WALLET_1,
    'select_google_wallet': CHAT_STAGES.USER_CREDENTIALS_WALLET_2,
    'select_paypal': CHAT_STAGES.USER_CREDENTIALS_WALLET_2,
    'allow_wallet_access': CHAT_STAGES.ASK_PAYMENT_METHOD,

    'enter_address': CHAT_STAGES.USER_CREDENTIALS_MANUAL_1,
    'enter_manual_address': CHAT_STAGES.USER_CREDENTIALS_MANUAL_2,
    'enter_email': CHAT_STAGES.ASK_PAYMENT_METHOD,

    'amex4444': CHAT_STAGES.CONFIRM_ORDER,
    'amex8888': CHAT_STAGES.CONFIRM_ORDER,

    'confirm_order': CHAT_STAGES.VERIFICATION_CODE,
    'enter_verification_code': CHAT_STAGES.ORDER_COMPLETED
   
  },
  disputing: {

  },
  
  hunter: {

  }
};

// Stage-specific options that appear after agent responses
// Important: keep option IDs in sync with CONVERSATION_FLOWS
export const STAGE_OPTIONS = {
  [CHAT_STAGES.ASK_INTENT]: [
    { id: 'coffee_maker', text: 'I\’m looking for a coffee maker specifically a glass french press. I don\’t have a preferred merchant, but I\’d like it to be refundable. Show me some options.' },
    { id: 'headphones', text: 'I\’m looking for gaming headphones with noise cancellation. They don’t need to be refundable, but I\’d like them from the merchant Amazon. Show me some options.' },
  ],

  [CHAT_STAGES.CONFIRM_INTENT]: [
    { id: 'confirm_intent', text: 'Yes, I confirm' },
  ],
  
  [CHAT_STAGES.SHOW_PRODUCTS]: [
    { id: 'select_product_1', text: 'Option 1 looks good' },
    { id: 'select_product_2', text: 'I want option 2' },
    { id: 'select_product_3', text: 'Option 3 please' }
  ],
  
  [CHAT_STAGES.ASK_USER_CREDENTIALS]: [
    { id: 'use_wallet', text: 'I want to use one of my digital wallets.' },
    { id: 'enter_address', text: 'Enter address manually' },
  ],

  [CHAT_STAGES.USER_CREDENTIALS_WALLET_1]: [
    {id: 'select_google_wallet', text: 'Google Wallet'},
    {id: 'select_paypal', text: 'PayPal'}
  ],
  [CHAT_STAGES.USER_CREDENTIALS_WALLET_2]: {
    select_google_wallet: [
      {id: 'allow_wallet_access', text: 'Yes, I allow Google Wallet to share my information with you.'}
    ],
    select_paypal: [
      {id: 'allow_wallet_access', text: 'Yes, I allow PayPal to share my information with you.'}
    ]
  },

  [CHAT_STAGES.USER_CREDENTIALS_MANUAL_1]: [
    {id: 'enter_manual_address', text: 'Recipient is Bugs Bunny and the address is 123 Main St, Sample City, ST 00000, US'},
  ],
  [CHAT_STAGES.USER_CREDENTIALS_MANUAL_2]: [
    {id: 'enter_email', text: 'Yes, I confirm. My email is bugsbunny@gmail.com'}
  ],

  [CHAT_STAGES.ASK_PAYMENT_METHOD]: [
    { id: 'amex4444', text: 'AMEX Card ending in 4444' },
    { id: 'amex8888', text: 'AMEX Card ending in 8888' },
  ],
  [CHAT_STAGES.CONFIRM_ORDER]: [
    { id: 'confirm_order', text: 'Yes, I confirm the purchase and order details.' },
  ],
  [CHAT_STAGES.VERIFICATION_CODE]: [
    { id: 'enter_verification_code', text: '123' },
  ],
  [CHAT_STAGES.ORDER_COMPLETED]: [],
  
  // Fallback options for any stage that doesn't have specific options defined
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
