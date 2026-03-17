import { journeys } from "@/lib/const/ux-writing";
import { createSlice } from "@reduxjs/toolkit";

const MandateLedgerSlice = createSlice({
  name: "MandateLedger",
  initialState: {
    journeysStatus: {
      [journeys.straightforward.id]: { 
        session_id: null, 
        user_id: null, 
        isInitializing: false,
        agentIsThinking: false,
        error: null
      },
      [journeys.hunter.id]: { 
        session_id: null, 
        user_id: null, 
        isInitializing: false,
        agentIsThinking: false,
        error: null
      },
      [journeys.disputing.id]: { 
        session_id: null, 
        user_id: null, 
        isInitializing: false,
        agentIsThinking: false,
        error: null
      },
    },
    healthStatus: null,
    /*
        {
            "status": "healthy",
            "timestamp": 1771514643.94278,
            "version": "0.1.0",
            "uptime_seconds": 67928.2084569931,
            "database": {
                "status": "healthy",
                "name": "mandate_ledger"
            },
            "environment": "development"
        }
        */
  },
  reducers: {
    setHealthStatus(state, action) {
      state.healthStatus = action.payload;
    },
    setSessionInitializing(state, action) {
      const { profileId } = action.payload;
      if (state.journeysStatus[profileId]) {
        state.journeysStatus[profileId].isInitializing = true;
      }
    },
    setSessionInitializationError(state, action) {
      const { profileId } = action.payload;
      if (state.journeysStatus[profileId]) {
        state.journeysStatus[profileId].isInitializing = false;
        state.journeysStatus[profileId].error = action.payload.error;
      }
    },
    setSessionId(state, action) {
      const { profileId, session_id, user_id } = action.payload;
      if (state.journeysStatus[profileId]) {
        state.journeysStatus[profileId].session_id = session_id;
        state.journeysStatus[profileId].user_id = user_id;
        state.journeysStatus[profileId].isInitializing = false;
        state.journeysStatus[profileId].error = null;
      }
    },
    setAgentThinking(state, action) {
      const { journeyId, agentIsThinking } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].agentIsThinking = agentIsThinking;
      }
    },
    clearSessionInitializing(state, action) {
      const { profileId } = action.payload;
      if (state.journeysStatus[profileId]) {
        state.journeysStatus[profileId].isInitializing = false;
        state.journeysStatus[profileId].error = null;
      }
    },
  },
});

export const { 
  setHealthStatus, 
  setSessionInitializing, 
  setSessionInitializationError,
  setSessionId,
  setAgentThinking,
  clearSessionInitializing 
} = MandateLedgerSlice.actions;

export default MandateLedgerSlice.reducer;
