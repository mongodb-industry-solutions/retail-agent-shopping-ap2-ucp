import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./globals.css";
import { Providers } from "./providers";

export const metadata = {
  title: "Agentic Commerce Demo",
  description: "Agentic Commerce Demo showcasing AP2 and Mandate Ledger Service integration",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
