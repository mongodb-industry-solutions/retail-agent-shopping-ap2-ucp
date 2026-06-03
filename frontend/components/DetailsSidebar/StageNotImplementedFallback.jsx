import React from 'react';
import { palette } from "@leafygreen-ui/palette";

// Static fallback component for unimplemented stages
const StageNotImplementedFallback = ({ step }) => (
  <div style={{ padding: '16px', color: palette.gray.dark2 }}>
    <p>Please select a valid "Behind the Scenes" step.</p>
    <small>Current Step "{step}"</small>
  </div>
);

export default StageNotImplementedFallback;