import { journeys } from "@/lib/const/ux-writing";
import { createSlice } from "@reduxjs/toolkit";
import { USER_ROLE, AGENT_ROLE } from "@/lib/const/bubbleDetails";

const GlobalSliceSlice = createSlice({
  name: "GlobalSlice",
  initialState: {
    isGuidedSliceOpened: true,
    followLatestMessage: true,
    sidebarWidth: 500,
    selectedMessage: null,
    startedJourneys: [],
    messages: {
      [`${journeys.straightforward.id}`]: [],
      [`${journeys.hunter.id}`]: [],
      [`${journeys.disputing.id}`]: [],
    },
  },
  reducers: {
    setGuidedSlice(state, action) {
      state.isGuidedSliceOpened = action.payload;
    },
    setFollowLatestMessage(state, action) {
      state.followLatestMessage = action.payload;
    },
    addStartedJourney(state, action) {
      const journeyId = action.payload;
      if (!state.startedJourneys.includes(journeyId)) {
        state.startedJourneys.push(journeyId);
      }
    },
    setSidebarWidth(state, action) {
      state.sidebarWidth = action.payload;
    },
    setSelectedMessage(state, action) {
      state.selectedMessage = action.payload;
    },
    addUserMessage(state, action) {
      const { journeyId, message, sessionId, userId, step, bubbleDetails, stepHasBehindTheScenes } = action.payload;
      const userMessage = {
        id: `user_${Date.now()}_${Math.random()}`,
        type: USER_ROLE,
        content: message,
        timestamp: new Date().toISOString(),
        sessionId,
        userId,
        step: step,
        bubbleDetails: bubbleDetails || null,
        stepHasBehindTheScenes: stepHasBehindTheScenes || false,
      };
      if (state.messages[journeyId]) {
        state.messages[journeyId].push(userMessage);
      }
      if (state.followLatestMessage && stepHasBehindTheScenes === true) {
        state.selectedMessage = userMessage;
      }
    },
    addAgentMessage(state, action) {
      const { journeyId, message, sessionId, userId, messageOptions, step, bubbleDetails, stepHasBehindTheScenes } = action.payload;
      const agentMessage = {
        id: `agent_${Date.now()}_${Math.random()}`,
        type: AGENT_ROLE, 
        content: message,
        timestamp: new Date().toISOString(),
        sessionId,
        userId,
        messageOptions: messageOptions || [],
        step: step,
        bubbleDetails: bubbleDetails || null,
        stepHasBehindTheScenes: stepHasBehindTheScenes || false,
      };
      if (state.messages[journeyId]) {
        state.messages[journeyId].push(agentMessage);
      }
      if (state.followLatestMessage && stepHasBehindTheScenes === true) {
        state.selectedMessage = agentMessage;
      }
    },
    setSessionIdToInitialUserMessage(state, action) {
      const { journeyId, sessionId } = action.payload;
      if (state.messages[journeyId]) {
        const firstUserMessage = state.messages[journeyId].find(message => message.type === USER_ROLE);
        if (firstUserMessage) {
          firstUserMessage.sessionId = sessionId;
        }
      }
    },
    clearMessages(state, action) {
      const { journeyId } = action.payload;
      if (state.messages[journeyId]) {
        state.messages[journeyId] = [];
      }
      // Also clear selected message when clearing messages  
      state.selectedMessage = null;
    }
  },
});

export const { 
  setGuidedSlice, 
  setFollowLatestMessage,
  addStartedJourney, 
  setSidebarWidth,
  setSelectedMessage,
  addUserMessage,
  addAgentMessage,
  setSessionIdToInitialUserMessage,
  clearMessages
} = GlobalSliceSlice.actions;

export default GlobalSliceSlice.reducer;
