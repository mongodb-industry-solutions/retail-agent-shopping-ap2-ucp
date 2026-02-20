import { createSlice } from "@reduxjs/toolkit";

const MandateLedgerSlice = createSlice({
  name: "MandateLedger",
  initialState: {
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
  },
});

export const { setHealthStatus } = MandateLedgerSlice.actions;

export default MandateLedgerSlice.reducer;
