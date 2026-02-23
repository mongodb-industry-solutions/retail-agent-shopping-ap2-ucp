import { createSlice } from "@reduxjs/toolkit";

const GuidedIntroSlice = createSlice({
  name: "GuidedIntro",
  initialState: {
    isGuidedSliceOpened: true,
  },
  reducers: {
    setGuidedSlice(state, action) {
      state.isGuidedSliceOpened = action.payload;
    },
  },
});

export const { setGuidedSlice } = GuidedIntroSlice.actions;

export default GuidedIntroSlice.reducer;
