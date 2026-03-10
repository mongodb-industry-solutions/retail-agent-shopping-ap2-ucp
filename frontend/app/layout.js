<<<<<<< HEAD
import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./globals.css";
import { Providers } from "./providers";

export const metadata = {
  title: "Agentic Commerce Demo",
  description: "Agentic Commerce Demo showcasing AP2 and Mandate Ledger Service integration",
=======
import "./globals.css";
import { Providers } from "./providers";

// TODO: Update metadata with actual demo details
export const metadata = {
  title: "Demo Template",
  description: "Industry Solutions Demo Template for NextJS",
>>>>>>> fb64d57ada70a720effbbcd1afd285744a243953
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
