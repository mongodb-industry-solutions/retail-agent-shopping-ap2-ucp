// Static imports for all Behind The Scenes stage components
import AskIntentStage from '@/components/BehindTheScenes/straightforward/AskIntentStage';

// Import shared styles
import './behindTheScenes.css';

// Component mapping: journey -> stage -> component
const componentMap = {
  straightforward: {
    ask_intent: AskIntentStage,
    // Add more stages as they are implemented:
    // confirm_intent: ConfirmIntentStage,
    // show_products: ShowProductsStage,
    // ask_user_credentials: AskUserCredentialsStage,
    // select_wallet: SelectWalletStage,
    // allow_wallet_access: AllowWalletAccessStage,
    // provide_address: ProvideAddressStage,
    // provide_email: ProvideEmailStage,
    // ask_payment_method: AskPaymentMethodStage,
    // confirm_order: ConfirmOrderStage,
    // verification_code: VerificationCodeStage,
    // order_completed: OrderCompletedStage,
  },
  
  hunter: {
    // Add hunter journey stage components here when implemented
  },
  
  disputing: {
    // Add disputing journey stage components here when implemented
  }
};

/**
 * Get the component for a specific journey and stage
 * @param {string} journey - The journey ID (straightforward, hunter, disputing)
 * @param {string} stage - The stage name (ask_intent, confirm_intent, etc.)
 * @returns {React.Component|null} The component or null if not found
 */
export const getStageComponent = (journey, stage) => {
  return componentMap[journey]?.[stage] || null;
};
