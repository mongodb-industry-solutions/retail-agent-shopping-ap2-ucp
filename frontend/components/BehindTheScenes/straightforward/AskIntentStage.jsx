import { USER_ROLE } from "@/lib/constants/messages";
import React from "react";
import ImageContainer from "../ImageContainer";
import { Code, Panel } from "@leafygreen-ui/code";

const wellKnownEndpointExample = {
  name: "Amazon Demo Store",
  ucp_version: "2026-01-11",

  services: {
    shopping: {
      transport: "rest",
      endpoint: "https://amazon.example.com/api/ucp",
    },
  },

  capabilities: [
    {
      name: "dev.ucp.shopping.checkout",
      version: "2026-01-11",
    },
    {
      name: "dev.ucp.shopping.ap2_mandate",
      version: "2026-01-11",
      extends: "dev.ucp.shopping.checkout",
    },
  ],

  payment_handlers: ["CARD", "GOOGLE_PAY"],

  signing_keys: [
    {
      kid: "amazon-key-2026",
      kty: "EC",
      crv: "P-256",
      x: "abc123...",
      y: "def456...",
    },
  ],
};

const AskIntentStage = ({ type }) => {
  return (
    <div>
      {type === USER_ROLE ? (
        <div>USER</div>
      ) : (
        <div>
          <ImageContainer
            src="/BehindTheScenes/straightforward/askIntentStage_agent_01.svg"
            alt="Meet Shopping agent"
          />

          <div className="info">
            <p>
              The agent you interact with to coordinate your purchase is what we
              call the <span className="purple-text">Shopping Agent</span>.
            </p>

            <p>
              It interprets your request, communicates with merchant agents to
              find products and offers, and coordinates the path from discovery
              to checkout.
            </p>

            <p>
              To do that, it relies on standardized protocols for
              agent-to-commerce interaction, such as UCP, the{" "}
              <a
                href="https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/"
                target="_blank"
              >
                Universal Commerce Protocol
              </a>
              .
            </p>

            <p>
              UCP allows the <span className="purple-text">Shopping Agent</span>{" "}
              to discover, through a standard <code>well-known endpoint</code>,
              what a merchant supports: commerce services, checkout
              capabilities, payment options, and secure{" "}
              <a href="https://ap2-protocol.org/" target="_blank">
                AP2 protocol
              </a>
              .
            </p>
          </div>

          <Code 
            style={{borderRadius: '0px'}} copyable="true" showLineNumbers expandable darkMode={true} 
            language="json" 
            collapsedLines={21}
            highlightLines={[15, 16, 17, 18, 19]}
            panel={<Panel title="Well-Known Endpoint Response" />}
        >
            {JSON.stringify(wellKnownEndpointExample, null, 2)}
          </Code>
          <div className="info">
            <p>
              This means the agent does not need a custom integration for every
              merchant. Instead, it can read the merchant’s published
              capabilities, understand how to interact with it, and, when AP2 is
              supported, move into an auditable transaction flow.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AskIntentStage;
