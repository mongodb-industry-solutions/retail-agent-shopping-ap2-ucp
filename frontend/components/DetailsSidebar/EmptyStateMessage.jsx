import React from 'react';
import { palette } from "@leafygreen-ui/palette";

// Static component for empty state when no message is selected
const EmptyStateMessage = () => (
  <div style={{ padding: '16px', color: palette.gray.dark1, textAlign: 'center' }}>
    Click on a message with behind the scenes info to see details here
  </div>
);

export default EmptyStateMessage;