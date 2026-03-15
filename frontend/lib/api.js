import store from '@/redux/store';
import { setSessionInitialationError, setSessionId, setAgentThinking } from '@/redux/slices/MandateLedgerSlice';
import { addUserMessage, addAgentMessage, setSessionIdToInitialUserMessage } from '@/redux/slices/GlobalSlice';
import { getChatOptions, getNextStage, INITIAL_USER_MESSAGE, CHAT_STAGES } from './chatOptions';
import { getDemoSessionId } from './helpers';

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
  console.log("getMandateLedgerServiceHealth res", data);
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
      userId: `${journeyId}-${demoSessionId}` // Use the constructed userId
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

  if (!response.ok) {
    const error = {
      error: true,
      message: `Error starting shopping session: ${response.status}`,
      status: response.status,
    };
    
    if (journeyId) {
      // Stop thinking state on error
      store.dispatch(setAgentThinking({
        journeyId: journeyId,
        agentIsThinking: false
      }));
      store.dispatch(setSessionInitialationError({ profileId: journeyId, error }));
    }
    
    return error;
  }

  const data = await response.json();
  console.log("startShoppingSession res", data);

  // Store session data in Redux
  if (journeyId && data.session_id) {
    store.dispatch(setSessionId({
      profileId: journeyId,
      session_id: data.session_id,
      user_id: data.user_id
    }));
    
    // Update the initial user message with the session ID
    store.dispatch(setSessionIdToInitialUserMessage({
      journeyId: journeyId,
      sessionId: data.session_id,
      userId: data.user_id
    }));
    
    // Stop thinking state
    store.dispatch(setAgentThinking({
      journeyId: journeyId,
      agentIsThinking: false
    }));
    
    // Add initial agent response with options
    const initialStage = CHAT_STAGES.INITIAL;
    const messageOptions = getChatOptions(initialStage);
    
    store.dispatch(addAgentMessage({
      journeyId: journeyId,
      message: data.initial_response,
      sessionId: data.session_id,
      userId: data.user_id,
      messageOptions,
      stage: initialStage
    }));
  }
  
  return data;
}

export async function chatWithShoppingAgentAPI(journeyId, message, selectedOptionId) {
  let demoSessionId = getDemoSessionId();
  let userId = `${journeyId}-${demoSessionId}`;
  let sessionId = store.getState().MandateLedger.journeysStatus[journeyId]?.session_id || null;
  let storedUserId = store.getState().MandateLedger.journeysStatus[journeyId]?.user_id || userId;
  if (!sessionId)
    console.log("Warning: No sessionId found in Redux for journeyId", journeyId);
  
  // Add user message immediately and set thinking state
  if (journeyId && sessionId) {
    store.dispatch(addUserMessage({
      journeyId: journeyId,
      message,
      sessionId,
      userId: storedUserId
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

  if (!response.ok) {
    const error = {
      error: true,
      message: `Error in chat: ${response.status}`,
      status: response.status,
    };
    
    // Stop thinking state on error
    if (journeyId) {
      store.dispatch(setAgentThinking({
        journeyId: journeyId,
        agentIsThinking: false
      }));
    }
    
    return error;
  }

  const data = await response.json();
  console.log("chatWithShoppingAgent res", data);
  
  // Process successful response
  if (journeyId && sessionId) {
    // Stop thinking state
    store.dispatch(setAgentThinking({
      journeyId: journeyId,
      agentIsThinking: false
    }));
    
    // Determine next stage based on selected option ID and journey type
    const nextStage = getNextStage(journeyId, selectedOptionId);
    
    // Get options for the next stage
    const messageOptions = getChatOptions(nextStage);
    
    // Add agent response with options
    store.dispatch(addAgentMessage({
      journeyId: journeyId,
      message: data.response,
      sessionId,
      userId: storedUserId,
      messageOptions,
      stage: nextStage
    }));
  }
  
  return data;
}