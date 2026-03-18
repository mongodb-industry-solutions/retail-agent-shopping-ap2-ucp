/**
 * Get or generate session ID for client-side tracking
 * IMPORTANT: This sessionId (sid) is different from SSE changeStreams sessionId and the session_id from the shopper conversation ID.
 * 
 * @returns {string} sid - Session ID from sessionStorage, generated if not exists
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

/**
 * Get current conversation stage from messages
 * @param {Object} state - Redux state
 * @param {string} journeyId - Journey identifier
 * @returns {string} Current stage or 'initial' if no messages
 */
export const getCurrentStage = (state, journeyId) => {
  const messages = state.messages[journeyId] || [];
  if (messages.length === 0) return 'initial';
  
  const lastMessage = messages[messages.length - 1];
  return lastMessage?.stage || 'initial';
};