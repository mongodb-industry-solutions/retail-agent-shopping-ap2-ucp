import store from "@/redux/store";
import {
  setSessionInitializationError,
  setJourneySessionAndUserId,
  setAgentThinking,
} from "@/redux/slices/MandateLedgerSlice";
import {
  addUserMessage,
  addAgentMessage,
  setSessionIdToInitialUserMessage,
} from "@/redux/slices/GlobalSlice";
import { getCurrentStep, getJourneyUserAndSessionId } from "./helpers";
import { USER_ROLE, AGENT_ROLE, getBubbleDetails } from "./const/bubbleDetails";
import { stepHasBehindTheScenes } from "@/components/BehindTheScenes/componentMap";
import { journeys } from "./const/ux-writing";

/**
 * Process agent response through assistant API to get step and messageOptions
 * @param {string} workflowId - The workflow identifier
 * @param {Array} conversation - Array of conversation messages
 * @returns {Promise<{step: string|null, messageOptions: Array}>} Assistant analysis result
 */
async function processAgentResponseWithAssistant(workflowId, conversation) {
  const maxRetries = 2;
  let lastError = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch("/api/assistant-step-calculation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          workflowId,
          conversation,
        }),
      });

      if (!response.ok) {
        lastError = new Error(`HTTP ${response.status}: ${response.statusText}`);
        console.error(`Assistant API error (attempt ${attempt + 1}/${maxRetries + 1}):`, response.status);
        
        // If this is not the last attempt, wait before retrying
        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1))); // Progressive delay: 1s, 2s
          continue;
        }
        
        // Last attempt failed - return fallback values
        console.error("All retry attempts failed. Using fallback values.");
        return { step: null, messageOptions: [], bubbleDetails: null };
      }

      // Successful response
      const data = await response.json();
      if (attempt > 0) {
        console.log(`Assistant API succeeded on attempt ${attempt + 1}`);
      }
      return {
        ...data,
        step: data.stepId || null,
        messageOptions: data.answers || [],
        bubbleDetails: getBubbleDetails(AGENT_ROLE, data.stepId) || null,
      };
    } catch (error) {
      lastError = error;
      console.error(`Network error calling assistant API (attempt ${attempt + 1}/${maxRetries + 1}):`, error);
      
      // If this is not the last attempt, wait before retrying
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1))); // Progressive delay: 1s, 2s
        continue;
      }
    }
  }

  // All attempts failed
  console.error("All retry attempts failed. Using fallback values. Last error:", lastError);
  return { step: null, messageOptions: [], bubbleDetails: null };
}

/**
 * Process successful agent response and dispatch to Redux
 */
async function processSuccessfulAgentResponse(
  journeyId,
  sessionId,
  userId,
  message,
  event_logs = [],
) {
  // Build conversation history for assistant API
  const messages = store.getState().Global.messages[journeyId] || [];
  const conversationHistory = buildConversationHistory([
    ...messages,
    {
      role: AGENT_ROLE,
      message: message,
      step: undefined, // CHECK This will be determined by assistant API
    },
  ]);

  // Get step and messageOptions from assistant API
  const { step, messageOptions, bubbleDetails } =
    await processAgentResponseWithAssistant(journeyId, conversationHistory);

  // Stop thinking state
  store.dispatch(
    setAgentThinking({
      journeyId: journeyId,
      agentIsThinking: false,
    }),
  );

  // Add agent response with dynamic options from assistant
  store.dispatch(
    addAgentMessage({
      journeyId: journeyId,
      message: message,
      sessionId: sessionId,
      userId: userId,
      messageOptions,
      step: step,
      bubbleDetails,
      stepHasBehindTheScenes: stepHasBehindTheScenes(
        journeyId,
        step,
        AGENT_ROLE,
      ),
      event_logs
    }),
  );
}

/**
 * Build conversation history from Redux messages for assistant API
 * @param {Array} messages - Messages from Redux state
 * @returns {Array} Formatted conversation history
 */
function buildConversationHistory(messages) {
  return messages.map((msg, index) => {
    const messageObj = {
      role: msg.role || msg.type,
      message: msg.message || msg.content,
    };

    // If it's the last message and it's an agent message, keep step undefined
    const isLastMessage = index === messages.length - 1;
    const isAgentMessage = msg.role === AGENT_ROLE || msg.type === AGENT_ROLE;

    if ((isLastMessage && isAgentMessage && msg.step === undefined) || messageObj.role !== AGENT_ROLE) {
      // Keep step undefined for the last agent message
      messageObj.step = undefined;
    } else {
      // Use existing step or default to "in-between-step"
      messageObj.step = msg.step || "in-between-step";
    }

    return messageObj;
  });
}

export async function startSessionAPI(journeyId, initialMessage = null) {
  let { userId } = getJourneyUserAndSessionId(journeyId);
  if(!initialMessage)
    initialMessage = journeys[journeyId]?.initialMessage || "Hello, I'd like to start shopping";

  console.log(`Starting session for journeyId=${journeyId}, userId=${userId}, initialMessage=${initialMessage}`);
  // Add initial user message immediately and set thinking state
  if (journeyId) {
    store.dispatch(
      addUserMessage({
        journeyId: journeyId,
        message: initialMessage,
        sessionId: null, // Will be updated when we get the session ID
        userId: userId, // Use the already constructed userId
        step: "initial",
        bubbleDetails: null,
        stepHasBehindTheScenes: stepHasBehindTheScenes(
          journeyId,
          "initial",
          USER_ROLE,
        ),
      }),
    );

    // Set agent thinking state
    store.dispatch(
      setAgentThinking({
        journeyId: journeyId,
        agentIsThinking: true,
      }),
    );
  }

  const endpoint =
    journeyId === journeys.disputing.id
      ? "/api/auditor-start-session"
      : "/api/shopping-start-session";
  const response = await fetch(
    `${endpoint}?user_id=${encodeURIComponent(userId)}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: initialMessage }),
    },
  );

  if (!response.ok)
    return handleApiError(
      journeyId,
      response.status,
      `Error starting session: ${response.status}`,
      true,
    );

  const data = await response.json();

  // Store session data in Redux
  if (journeyId && data.session_id) {
    store.dispatch(
      setJourneySessionAndUserId({
        journeyId,
        session_id: data.session_id,
        user_id: data.user_id,
      }),
    );

    // Update the initial user message with the session ID
    store.dispatch(
      setSessionIdToInitialUserMessage({
        journeyId: journeyId,
        sessionId: data.session_id,
        userId: data.user_id,
      }),
    );

    await processSuccessfulAgentResponse(
      journeyId,
      data.session_id,
      data.user_id,
      data.initial_response,
      data.event_logs || [],
    );
  }

  return data;
}

export async function chatWithShoppingAgentAPI(journeyId, message) {
  let { userId, sessionId } = getJourneyUserAndSessionId(journeyId);
  if (!sessionId)
    console.log(
      "Warning: No sessionId found in Redux for journeyId",
      journeyId,
    );

  // Add user message immediately and set thinking state
  if (journeyId && sessionId) {
    // Get current step from Redux state - this might be null, which is fine
    const currentStep = getCurrentStep(store.getState().Global, journeyId);

    store.dispatch(
      addUserMessage({
        journeyId: journeyId,
        message,
        sessionId,
        userId,
        step: currentStep,
        bubbleDetails: null, // User messages don't get bubbleDetails from assistant API
        stepHasBehindTheScenes: stepHasBehindTheScenes(
          journeyId,
          currentStep,
          USER_ROLE,
        ),
      }),
    );

    // Set agent thinking state
    store.dispatch(
      setAgentThinking({
        journeyId: journeyId,
        agentIsThinking: true,
      }),
    );
  }

  const response = await fetch(`/api/shopping-chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      user_id: userId,
      session_id: sessionId,
    }),
  });

  if (!response.ok)
    return handleApiError(
      journeyId,
      response.status,
      `Error in chat: ${response.status}`,
      false,
    );

  const data = await response.json();

  // Process successful response
  if (journeyId && sessionId) {
    await processSuccessfulAgentResponse(
      journeyId,
      sessionId,
      userId,
      data.response,
      data.event_logs || [],
    );
  }

  return data;
}

export async function chatWithAuditorAgentAPI(journeyId, message) {
  let { userId, sessionId } = getJourneyUserAndSessionId(journeyId);
  if (!sessionId)
    console.log(
      "Warning: No sessionId found in Redux for journeyId",
      journeyId,
    );

  // Add user message immediately and set thinking state
  if (journeyId && sessionId) {
    // Get current step from Redux state - this might be null, which is fine
    const currentStep = getCurrentStep(store.getState().Global, journeyId);

    store.dispatch(
      addUserMessage({
        journeyId: journeyId,
        message,
        sessionId,
        userId,
        step: currentStep,
        bubbleDetails: null, // User messages don't get bubbleDetails from assistant API
        stepHasBehindTheScenes: stepHasBehindTheScenes(
          journeyId,
          currentStep,
          USER_ROLE,
        ),
      }),
    );

    // Set agent thinking state
    store.dispatch(
      setAgentThinking({
        journeyId: journeyId,
        agentIsThinking: true,
      }),
    );
  }

  const response = await fetch(`/api/auditor-chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      user_id: userId,
      session_id: sessionId,
    }),
  });

  if (!response.ok)
    return handleApiError(
      journeyId,
      response.status,
      `Error in chat: ${response.status}`,
      false,
    );

  const data = await response.json();

  // Process successful response
  if (journeyId && sessionId) {
    await processSuccessfulAgentResponse(
      journeyId,
      sessionId,
      userId,
      data.response,
      data.event_logs || [],
    );
  }

  return data;
}

const handleApiError = (
  journeyId,
  responseStatus,
  errorMessage,
  dispatchSessionError = false,
) => {
  const error = {
    error: true,
    message: errorMessage,
    status: responseStatus,
  };

  if (journeyId) {
    // Stop thinking state on error
    store.dispatch(
      setAgentThinking({
        journeyId: journeyId,
        agentIsThinking: false,
      }),
    );

    if (dispatchSessionError) {
      store.dispatch(setSessionInitializationError({ journeyId, error }));
    }
  }

  return error;
};
