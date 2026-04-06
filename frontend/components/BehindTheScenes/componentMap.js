// Static imports for all Behind The Scenes step components
import ShoppingAgentIntroductionStep from '@/components/BehindTheScenes/straightforward/ShoppingAgentIntroductionStep';
import MerchantAgentIntroductionStep from '@/components/BehindTheScenes/straightforward/MerchantAgentIntroductionStep';
import MandatesCreatedStep from '@/components/BehindTheScenes/straightforward/MandatesCreatedStep';
import PaymentCompletedStep from '@/components/BehindTheScenes/straightforward/PaymentCompletedStep';
import CartMandateSignedPaymentCredentialsStep from './straightforward/CartMandateSignedPaymentCredentialsStep';

// Import shared styles
import './behindTheScenes.css';
import { CHAT_STEPS } from '@/lib/const/steps';

// Component mapping: workflow -> step -> component
const componentMap = {
  straightforward: {
    [CHAT_STEPS.SHOPPING_AGENT_INTRODUCTION]: ShoppingAgentIntroductionStep,
    [CHAT_STEPS.MERCHANT_AGENT_INTRODUCTION]: MerchantAgentIntroductionStep,
    [CHAT_STEPS.MANDATES_CREATED]: MandatesCreatedStep,
    [CHAT_STEPS.CART_MANDATE_SIGNED_PAYMENT_CREDENTIALS]: CartMandateSignedPaymentCredentialsStep,
    [CHAT_STEPS.PAYMENT_COMPLETED]: PaymentCompletedStep,
  },
  
  hunter: {
    // Add hunter workflow step components here when implemented
  },
  
  disputing: {
    // Add disputing workflow step components here when implemented
  }
};

/**
 * Get the component for a specific journeyId and step
 * @param {string} journeyId - The journey ID (straightforward, hunter, disputing)
 * @param {string} step - The step name from CHAT_STEPS
 * @returns {React.Component|null} The component or null if not found
 */
export const getStepComponent = (journeyId, step) => {
  return componentMap[journeyId]?.[step] || null;
};

export const stepHasBehindTheScenes = (journeyId, step) => {
  return !!componentMap[journeyId]?.[step];
};