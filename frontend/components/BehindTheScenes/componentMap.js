// Static imports for all Behind The Scenes step components
import ShoppingAgentIntroductionStep from '@/components/BehindTheScenes/straightforward/ShoppingAgentIntroductionStep';
import MerchantAgentIntroductionStep from '@/components/BehindTheScenes/straightforward/MerchantAgentIntroductionStep';
import MandatesCreatedStep from '@/components/BehindTheScenes/straightforward/MandatesCreatedStep';
import PaymentCompletedStep from '@/components/BehindTheScenes/straightforward/PaymentCompletedStep';
import CartMandateSignedPaymentCredentialsStep from './straightforward/CartMandateSignedPaymentCredentialsStep';

// Hunter workflow components
import FirstHunterIntentCreatedStep from '@/components/BehindTheScenes/hunter/FirstHunterIntentCreatedStep';
import { HunterIntentImmutabilityStep } from './hunter/HunterIntentImmutabilityStep';
import SecondHunterIntentCreatedStep from '@/components/BehindTheScenes/hunter/SecondHunterIntentCreatedStep';
import HunterCardPurchaseChangeStep from '@/components/BehindTheScenes/hunter/HunterCardPurchaseChangeStep';
import HunterQuestionsIdempotencyStep from '@/components/BehindTheScenes/hunter/HunterQuestionsIdempotencyStep';

// Import shared styles
import './behindTheScenes.css';
import { CHAT_STEPS } from '@/lib/const/steps';
import { USER_ROLE } from '@/lib/const/bubbleDetails';

// Component mapping: workflow -> step -> component
const componentMap = {
  straightforward: {
    [CHAT_STEPS.SHOPPING_AGENT_INTRODUCTION]: ShoppingAgentIntroductionStep,
    [CHAT_STEPS.MERCHANT_AGENT_INTRODUCTION]: MerchantAgentIntroductionStep,
    [CHAT_STEPS.MANDATES_CREATED]: MandatesCreatedStep,
    [CHAT_STEPS.CART_MANDATE_SIGNED_PAYMENT_CREDENTIALS]: CartMandateSignedPaymentCredentialsStep,
    [CHAT_STEPS.PAYMENT_COMPLETED]: PaymentCompletedStep
  },
  
  hunter: {
    [CHAT_STEPS.FIRST_HUNTER_INTENT_CREATED]: FirstHunterIntentCreatedStep,
    [CHAT_STEPS.HUNTER_INTENT_IMMUTABILITY]: HunterIntentImmutabilityStep,
    [CHAT_STEPS.SECOND_HUNTER_INTENT_CREATED]: SecondHunterIntentCreatedStep,
    [CHAT_STEPS.HUNTER_CARD_PURCHASE_CHANGE]: HunterCardPurchaseChangeStep,
    [CHAT_STEPS.HUNTER_QUESTIONS_IDEMPOTENCY]: HunterQuestionsIdempotencyStep
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

export const stepHasBehindTheScenes = (journeyId, step, type) => {
  // user type messages do not have behind the scenes, so we only check for agent messages
  return (type !== USER_ROLE) && !!componentMap[journeyId]?.[step];
};