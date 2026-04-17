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
        error: null,
        cartMandates: [],
        cartMandateWithTwoSignatures: null,
        paymentMandate: null,
        paymentDocument: null,
      },
      [journeys.hunter.id]: {
        session_id: null,
        user_id: null,
        isInitializing: false,
        agentIsThinking: false,
        error: null,
        paymentDocument: null,
        intentMandates: [null, null], // to store multiple intent mandates if needed, initialized with 2 slots for the hunter journey
      },
      [journeys.disputing.id]: {
        session_id: null,
        user_id: null,
        isInitializing: false,
        agentIsThinking: false,
        error: null,
        order: null, // an item with structure {payment: {...}, mandate: {...}}
      },
    },
    healthStatus: null,
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
    setJourneySessionAndUserId(state, action) {
      const { journeyId, session_id, user_id } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].session_id = session_id;
        state.journeysStatus[journeyId].user_id = user_id;
        state.journeysStatus[journeyId].isInitializing = false;
        state.journeysStatus[journeyId].error = null;
      }
    },
    setJourneyUserId(state, action) {
      const { journeyId, user_id } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].user_id = user_id;
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
    setCartMandates(state, action) {
      const { journeyId, cartMandates } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].cartMandates = [...cartMandates];
      }
    },
    setCartMandatesWithTwoSignatures(state, action) {
      const { journeyId, cartMandateWithTwoSignatures } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].cartMandateWithTwoSignatures =
          cartMandateWithTwoSignatures;
      }
    },
    setPaymentMandate(state, action) {
      const { journeyId, paymentMandate } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].paymentMandate = paymentMandate;
      }
    },
    setPaymentDocument(state, action) {
      const { journeyId, paymentDocument } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].paymentDocument = paymentDocument;
      }
    },
    setOrder(state, action) {
      const { journeyId, order } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].order = order;
      }
    },
    setIntentMandate(state, action) {
      const { journeyId, intentMandate, index = 0 } = action.payload;
      if (state.journeysStatus[journeyId]) {
        state.journeysStatus[journeyId].intentMandates[index] = intentMandate;
      }
    }
  },
});

export const {
  setHealthStatus,
  setSessionInitializing,
  setSessionInitializationError,
  setJourneySessionAndUserId,
  setAgentThinking,
  clearSessionInitializing,
  setCartMandates,
  setCartMandatesWithTwoSignatures,
  setJourneyUserId,
  setPaymentMandate,
  setPaymentDocument,
  setOrder,
  setIntentMandate
} = MandateLedgerSlice.actions;

export default MandateLedgerSlice.reducer;
