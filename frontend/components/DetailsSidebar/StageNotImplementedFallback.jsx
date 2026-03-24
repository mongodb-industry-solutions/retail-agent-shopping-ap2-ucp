import React from 'react';
import { palette } from "@leafygreen-ui/palette";

// Static fallback component for unimplemented stages
const StageNotImplementedFallback = ({ stage, behindTheScenes }) => (
  <div style={{ padding: '16px', color: palette.gray.dark2 }}>
    <p>Behind the scenes component for stage "{stage}" not yet implemented.</p>
    <details style={{ marginTop: '8px' }}>
      <summary style={{ cursor: 'pointer' }}>Raw data:</summary>
      <pre style={{ 
        background: palette.gray.light3, 
        padding: '8px', 
        borderRadius: '4px',
        fontSize: '12px',
        marginTop: '8px',
        overflow: 'auto'
      }}>
        {JSON.stringify(behindTheScenes, null, 2)}
      </pre>
    </details>
  </div>
);

export default StageNotImplementedFallback;