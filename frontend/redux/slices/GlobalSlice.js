import { createSlice } from "@reduxjs/toolkit";

const GlobalSliceSlice = createSlice({
  name: "GlobalSlice",
  initialState: {
    isGuidedSliceOpened: false, //TODO, change to true after this feature is done
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
