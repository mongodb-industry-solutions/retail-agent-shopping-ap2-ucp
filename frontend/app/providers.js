"use client";

import LeafyGreenProvider from "@leafygreen-ui/leafygreen-provider";
import ClientProvider from "./ClientProvider";

export function Providers({ children }) {
  return (
    <ClientProvider>
      <LeafyGreenProvider>{children}</LeafyGreenProvider>
    </ClientProvider>
  );
}
