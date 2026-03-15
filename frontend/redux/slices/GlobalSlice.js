import { journeys } from "@/lib/const/ux-writing";
import { createSlice } from "@reduxjs/toolkit";
import { USER_ROLE, AGENT_ROLE } from "@/lib/constants/messages";

const GlobalSliceSlice = createSlice({
  name: "GlobalSlice",
  initialState: {
    isGuidedSliceOpened: true,
    sidebarWidth: 420,
    startedJourneys: [],
    messages: {
      [`${journeys.straightforward.id}`]: [],
      [`${journeys.hunter.id}`]: [],
      [`${journeys.disputing.id}`]: [],
    },
    chatStage: {
      [`${journeys.straightforward.id}`]: 'initial',
      [`${journeys.hunter.id}`]: 'initial', 
      [`${journeys.disputing.id}`]: 'initial',
    }
  },
  reducers: {
    setGuidedSlice(state, action) {
      state.isGuidedSliceOpened = action.payload;
    },
    addStartedJourney(state, action) {
      const profileId = action.payload;
      if (!state.startedJourneys.includes(profileId)) {
        state.startedJourneys.push(profileId);
      }
    },
    setSidebarWidth(state, action) {
      state.sidebarWidth = action.payload;
    },
    addUserMessage(state, action) {
      const { journeyId, message, sessionId, userId } = action.payload;
      const userMessage = {
        id: `user_${Date.now()}_${Math.random()}`,
        type: USER_ROLE,
        content: message,
        timestamp: new Date().toISOString(),
        sessionId,
        userId
      };
      if (state.messages[journeyId]) {
        state.messages[journeyId].push(userMessage);
      }
    },
    addAgentMessage(state, action) {
      const { journeyId, message, sessionId, userId, messageOptions, stage } = action.payload;
      const agentMessage = {
        id: `agent_${Date.now()}_${Math.random()}`,
        type: AGENT_ROLE, 
        content: message,
        timestamp: new Date().toISOString(),
        sessionId,
        userId,
        messageOptions: messageOptions || [],
        stage: stage || 'general'
      };
      if (state.messages[journeyId]) {
        state.messages[journeyId].push(agentMessage);
      }
      if (stage && state.chatStage[journeyId] !== undefined) {
        state.chatStage[journeyId] = stage;
      }
    },
    setChatStage(state, action) {
      const { profileId, stage } = action.payload;
      if (state.chatStage[profileId] !== undefined) {
        state.chatStage[profileId] = stage;
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
      const { profileId } = action.payload;
      if (state.messages[profileId]) {
        state.messages[profileId] = [];
      }
      if (state.chatStage[profileId] !== undefined) {
        state.chatStage[profileId] = 'initial';
      }
    }
  },
});

export const { 
  setGuidedSlice, 
  addStartedJourney, 
  setSidebarWidth,
  addUserMessage,
  addAgentMessage,
  setChatStage,
  setSessionIdToInitialUserMessage,
  clearMessages
} = GlobalSliceSlice.actions;

export default GlobalSliceSlice.reducer;
