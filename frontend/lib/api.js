import store from '@/redux/store';
import { setSessionInitializationError, setSessionId, setAgentThinking } from '@/redux/slices/MandateLedgerSlice';
import { addUserMessage, addAgentMessage, setSessionIdToInitialUserMessage } from '@/redux/slices/GlobalSlice';
import { INITIAL_USER_MESSAGE } from './const/steps';
import { getDemoSessionId, getCurrentStage } from './helpers';
import { USER_ROLE, AGENT_ROLE, getBubbleDetails } from './const/bubbleDetails';

/**
 * Process agent response through assistant API to get step and messageOptions
 * @param {string} workflowId - The workflow identifier
 * @param {Array} conversation - Array of conversation messages
 * @returns {Promise<{step: string|null, messageOptions: Array}>} Assistant analysis result
 */
async function processAgentResponseWithAssistant(workflowId, conversation) {
  try {
    const response = await fetch('/api/assistant-step-calculation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        workflowId,
        conversation
      })
    });

    if (!response.ok) {
      console.error('Error calling assistant API:', response.status);
      // Return fallback values on API error
      return { step: null, messageOptions: [], bubbleDetails: null };
    }

    const data = await response.json();
    return {
      ...data,
      step: data.stepId || null,
      messageOptions: data.answers || [],
      bubbleDetails: getBubbleDetails(AGENT_ROLE, data.stepId) || null
    };
  } catch (error) {
    console.error('Error processing assistant API response:', error);
    // Return fallback values on network error
    return { step: null, messageOptions: [], bubbleDetails: null };
  }
}

/**
 * Process successful agent response and dispatch to Redux
 */
async function processSuccessfulAgentResponse(journeyId, sessionId, userId, message) {
  // Stop thinking state
  store.dispatch(setAgentThinking({
    journeyId: journeyId,
    agentIsThinking: false
  }));
  
  // Build conversation history for assistant API
  const messages = store.getState().Global.messages[journeyId] || [];
  const conversationHistory = buildConversationHistory([
    ...messages,
    {
      type: AGENT_ROLE,
      content: message,
      stage: undefined  // This will be determined by assistant API
    }
  ]);
  
  // Get step and messageOptions from assistant API
  const { step, messageOptions, bubbleDetails } = await processAgentResponseWithAssistant(journeyId, conversationHistory);
  
  // Add agent response with dynamic options from assistant
  store.dispatch(addAgentMessage({
    journeyId: journeyId,
    message: message,
    sessionId: sessionId,
    userId: userId,
    messageOptions,
    step: step,
    bubbleDetails,
  }));
}

/**
 * Build conversation history from Redux messages for assistant API
 * @param {Array} messages - Messages from Redux state
 * @returns {Array} Formatted conversation history
 */
function buildConversationHistory(messages) {
  return messages.map(msg => {
    const messageObj = {
      role: msg.type,
      message: msg.content
    };
    
    // Add step to agent messages if it exists
    if (msg.type === AGENT_ROLE && msg.step) {
      messageObj.step = msg.step;
    }
    
    return messageObj;
  });
}

export async function getMandateLedgerServiceHealthAPI() {
  const response = await fetch(`/api/mandateLedgerServiceHealth`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    return {
      error: true,
      message: `Error fetching mandate ledger service health: ${response.status}`,
      status: response.status,
    };
  }
  let data = await response.json();
  return data;
}

export async function startShoppingSessionAPI(journeyId) {
  let demoSessionId = getDemoSessionId();
  let userId = `${journeyId}-${demoSessionId}`;
  
  // Add initial user message immediately and set thinking state
  if (journeyId) {
    store.dispatch(addUserMessage({
      journeyId: journeyId,
      message: INITIAL_USER_MESSAGE,
      sessionId: null, // Will be updated when we get the session ID
      userId: userId, // Use the already constructed userId
      step: 'initial',
      bubbleDetails: null,
    }));
    
    // Set agent thinking state
    store.dispatch(setAgentThinking({
      journeyId: journeyId,
      agentIsThinking: true
    }));
  }
  
  const response = await fetch(`/api/shopping-start-session?user_id=${encodeURIComponent(userId)}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id: userId }),
  });

  if (!response.ok)
    return handleApiError(journeyId, response.status, `Error starting shopping session: ${response.status}`, true);

  const data = await response.json();

  // Store session data in Redux
  if (journeyId && data.session_id) {
    store.dispatch(setSessionId({
      journeyId,
      session_id: data.session_id,
      user_id: data.user_id
    }));
    
    // Update the initial user message with the session ID
    store.dispatch(setSessionIdToInitialUserMessage({
      journeyId: journeyId,
      sessionId: data.session_id,
      userId: data.user_id
    }));
    
    await processSuccessfulAgentResponse(
      journeyId,
      data.session_id,
      data.user_id,
      data.initial_response
    );
  }
  
  return data;
}

export async function chatWithShoppingAgentAPI(journeyId, message) {
  let demoSessionId = getDemoSessionId();
  let userId = `${journeyId}-${demoSessionId}`;
  let sessionId = store.getState().MandateLedger.journeysStatus[journeyId]?.session_id || null;
  let storedUserId = store.getState().MandateLedger.journeysStatus[journeyId]?.user_id || userId;
  if (!sessionId)
    console.log("Warning: No sessionId found in Redux for journeyId", journeyId);
  
  // Add user message immediately and set thinking state
  if (journeyId && sessionId) {
    // Get current step from Redux state - this might be null, which is fine
    const currentStep = getCurrentStage(store.getState().Global, journeyId);
    
    store.dispatch(addUserMessage({
      journeyId: journeyId,
      message,
      sessionId,
      userId: storedUserId,
      step: currentStep,
      bubbleDetails: null, // User messages don't get bubbleDetails from assistant API
      behindTheScenes: null // User messages don't get behindTheScenes from assistant API
    }));
    
    // Set agent thinking state
    store.dispatch(setAgentThinking({
      journeyId: journeyId,
      agentIsThinking: true
    }));
  }
  
  const response = await fetch(`/api/shopping-chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body:JSON.stringify({
      message: message,
      user_id: userId,
      session_id: sessionId
    })
  });

  if (!response.ok)
    return handleApiError(journeyId, response.status, `Error in chat: ${response.status}`, false);

  const data = await response.json();
  
  // Process successful response
  if (journeyId && sessionId) {
    await processSuccessfulAgentResponse(
      journeyId,
      sessionId,
      storedUserId,
      data.response
    );
  }
  
  return data;
}

const handleApiError = (journeyId, responseStatus, errorMessage, dispatchSessionError = false) => {
  const error = {
    error: true,
    message: errorMessage,
    status: responseStatus,
  };
  
  if (journeyId) {
    // Stop thinking state on error
    store.dispatch(setAgentThinking({
      journeyId: journeyId,
      agentIsThinking: false
    }));
    
    if (dispatchSessionError) {
      store.dispatch(setSessionInitializationError({ journeyId, error }));
    }
  }
  
  return error;
}