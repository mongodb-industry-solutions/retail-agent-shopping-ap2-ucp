import React from 'react';
import { palette } from "@leafygreen-ui/palette";

// Static fallback component for unimplemented stages
const StageNotImplementedFallback = ({ stage }) => (
  <div style={{ padding: '16px', color: palette.gray.dark2 }}>
    <p>Behind the scenes component for stage "{stage}" not yet implemented.</p>
  </div>
);

export default StageNotImplementedFallback;