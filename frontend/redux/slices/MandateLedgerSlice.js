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
      const { journeyId } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].isInitializing = true;
      }
    },
    setSessionInitializationError(state, action) {
      const { journeyId } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].isInitializing = false;
        state.journeysStatus[journeyId].error = action.payload.error;
      }
    },
    setSessionId(state, action) {
      const { journeyId, session_id, user_id } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].session_id = session_id;
        state.journeysStatus[journeyId].user_id = user_id;
        state.journeysStatus[journeyId].isInitializing = false;
        state.journeysStatus[journeyId].error = null;
      }
    },
    setAgentThinking(state, action) {
      const { journeyId, agentIsThinking } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].agentIsThinking = agentIsThinking;
      }
    },
    clearSessionInitializing(state, action) {
      const { journeyId } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].isInitializing = false;
        state.journeysStatus[journeyId].error = null;
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
