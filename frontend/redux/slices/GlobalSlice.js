<<<<<<< HEAD
import { profiles } from "@/lib/const/ux-writing";
import { createSlice } from "@reduxjs/toolkit";

const GlobalSliceSlice = createSlice({
  name: "GlobalSlice",
  initialState: {
    isGuidedSliceOpened: true,
    sidebarWidth: 420,
    startedJourneys: [],
    messages: {
      [`${profiles.straightforward.id}`]: [],
      [`${profiles.hunter.id}`]: [],
      [`${profiles.disputing.id}`]: [],
    },
=======
import { createSlice } from "@reduxjs/toolkit";

const GuidedIntroSlice = createSlice({
  name: "GuidedIntro",
  initialState: {
    isGuidedSliceOpened: true,
>>>>>>> fb64d57ada70a720effbbcd1afd285744a243953
  },
  reducers: {
    setGuidedSlice(state, action) {
      state.isGuidedSliceOpened = action.payload;
    },
<<<<<<< HEAD
    addStartedJourney(state, action) {
      const profileId = action.payload;
      if (!state.startedJourneys.includes(profileId)) {
        state.startedJourneys.push(profileId);
      }
    },
    setSidebarWidth(state, action) {
      state.sidebarWidth = action.payload;
    },
  },
});

export const { 
  setGuidedSlice, 
  addStartedJourney, 
  setSidebarWidth 
} = GlobalSliceSlice.actions;

export default GlobalSliceSlice.reducer;
=======
  },
});

export const { setGuidedSlice } = GuidedIntroSlice.actions;

export default GuidedIntroSlice.reducer;
>>>>>>> fb64d57ada70a720effbbcd1afd285744a243953
