import { createSlice } from "@reduxjs/toolkit";

const GlobalSliceSlice = createSlice({
  name: "GlobalSlice",
  initialState: {
    isGuidedSliceOpened: true,
    startedJourneys: [],
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
  },
});

export const { setGuidedSlice, addStartedJourney } = GlobalSliceSlice.actions;

export default GlobalSliceSlice.reducer;
