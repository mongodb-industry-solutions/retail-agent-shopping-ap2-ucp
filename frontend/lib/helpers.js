/**
 * Get or generate session ID for client-side tracking
 * IMPORTANT: This sessionId (sid) is different from SSE changeStreams sessionId and the session_id from the shopper conversation ID.
 * 
 * @returns {Object} Object containing { sid, uid }
 * @returns {string} sid - Session ID from sessionStorage, generated if not exists
 * @returns {string|null} uid - User ID from Redux store selectedUser
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