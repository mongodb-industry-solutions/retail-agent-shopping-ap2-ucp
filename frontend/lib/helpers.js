import { setJourneyUserId } from "@/redux/slices/MandateLedgerSlice";
import store from "@/redux/store";

/**
 * Get or generate session ID for client-side tracking
 * IMPORTANT: This sessionId (sid) is different from SSE changeStreams sessionId and the session_id from the shopper conversation ID.
 * 
 * @returns {string} sid - Session ID from sessionStorage, generated if not exists
 * Note: This is used for client-side tracking and should not be confused with backend session identifiers.
 * This demo session id is used to construct the user_id of each journey by doing <journey>-<demoSessionId>
*/
export const getDemoSessionId = () => {
  // Get or generate sessionId (sid) - stored in sessionStorage
  let sid = sessionStorage.getItem('sid');
  if (!sid) {
    sid = crypto.randomUUID();
    sessionStorage.setItem('sid', sid);
  }

  return sid;
};

export const getJourneyUserAndSessionId = (journeyId) => {
  const journeyStatus = store.getState().MandateLedger.journeysStatus[journeyId] || {};
  const sessionId = journeyStatus?.session_id || null; // session_id comes from the start-session API to the agents
  let userId = journeyStatus?.user_id || null;
  if(!userId) {
    userId = `${journeyId}-${getDemoSessionId()}`;
    store.dispatch(setJourneyUserId({
      journeyId,
      user_id: userId
    }));
  }
  return { sessionId, userId };
};

/**
 * Get current conversation step from messages
 * @param {Object} reduxState - Redux state
 * @param {string} journeyId - Journey identifier
 * @returns {string} Current step or 'initial' if no messages
 */
export const getCurrentStep = (reduxState, journeyId) => {
  const messages = reduxState.messages[journeyId] || [];
  if (messages.length === 0) return 'initial';
  
  const lastMessage = messages[messages.length - 1];
  return lastMessage?.step || 'initial';
};