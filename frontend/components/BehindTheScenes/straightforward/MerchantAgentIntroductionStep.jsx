import React from "react";
import ImageContainer from "../ImageContainer";
import {Banner} from "@leafygreen-ui/banner";

const MerchantAgentIntroductionStep = () => {
  return (
    <div>
      <div className="info">
        <p>
          At this point, the <span className="purple-text">Shopping Agent</span>{" "}
          has already captured the user’s request and identified a{" "}
          <span className="green-text">Merchant Agent</span> that can respond
          with relevant purchase options.
        </p>
      </div>
      <ImageContainer
        src="/BehindTheScenes/straightforward/MerchantAgentIntroductionStep_01.svg"
        alt="Meet Merchant Agent"
      />
      <div className="info">
        <p>
          To exchange that request, the agents communicate through an
          agent-to-agent protocol (
          <a
            href="https://a2a-protocol.org/latest/topics/what-is-a2a"
            target="_blank"
            rel="noopener noreferrer"
          >
            A2A
          </a>
          ).
        </p>
        <p>
          The A2A Protocol provides standard methods and data structures for
          agents to communicate with one another, regardless of their underlying
          implementation, so the same agents can be used as an interconnected
          system, communicating seamlessly through the standardized protocol.
        </p>
        <p>
          As part of that interaction, the{" "}
          <span className="purple-text">Shopping Agent</span> needs to send the
          user’s purchase intent to the{" "}
          <span className="green-text">Merchant Agent</span>, packaged as a
          <strong>Mandate</strong> — one of the core building blocks of the{" "}
          <strong>AP2 protocol</strong>.
        </p>
      </div>
      <div className="d-flex flex-column gap-4">
        <ImageContainer
          src="/BehindTheScenes/straightforward/MerchantAgentIntroductionStep_02.svg"
          alt="Meet Cryptographic Mandates"
        />
        <Banner variant="info" className="mb-3" style={{ fontSize: "16px" }}>
          <p>
            In AP2, trust is established through mandates and{" "}
            <a
              href="https://www.okta.com/es-es/identity-101/what-are-verifiable-digital-credentials/"
              target="_blank"
              rel="noopener noreferrer"
            >
              Verifiable Digital Credentials (VDCs)
            </a>
            : standardized data structures used to convey trusted information between agents.
          </p>
        </Banner>
        <div className="info">
          <p>
            They are tamper-evident, non-disputable, portable, and cryptographically signed digital objects that serve as the building blocks of a transaction.
          </p>
          <p>
            The primary VDCs in this framework are the Intent Mandate, the Cart Mandate, and the Payment Mandate. Each one plays a distinct role in establishing trust:
          </p>
          <ul className="list-disc list-inside space-y-1 text-left">
            <li>The <a href="https://ap2-protocol.org/specification/#412-the-intent-mandate" target="_blank" rel="noopener noreferrer">Intent Mandate</a> captures and proves the user's intent</li>
            <li>The <a href="https://ap2-protocol.org/specification/#411-the-cart-mandate" target="_blank" rel="noopener noreferrer">Cart Mandate</a> defines the exact transaction the merchant commits to fulfill</li>
            <li>The <a href="https://ap2-protocol.org/specification/#413-the-payment-mandate-for-ai-agent-visibility-to-payments-ecosystem" target="_blank" rel="noopener noreferrer">Payment Mandate</a> provides trusted visibility of the transaction to the payments ecosystem.</li>
          </ul>
        </div>
        <ImageContainer
          className="mt-4"
          src="/BehindTheScenes/straightforward/MerchantAgentIntroductionStep_03.svg"
          alt="Meet Mandate Communication"
        />
      </div>
      <div className="info">
        <p>
          At this point in the flow, the{" "}
          <span className="purple-text">Shopping Agent</span> signs the{" "}
          <strong>Intent Mandate</strong> using VDCs, as required by
          the <strong>AP2 protocol</strong>, to generate verifiable proof of the
          user’s explicit intent. In this way, it is no longer just a simple
          message but becomes a verifiable instruction that the{" "}
          <span className="green-text">Merchant Agent</span> can validate and
          securely store for future audits, preserving trustworthy evidence of
          the user’s intent.
        </p>
      </div>
    </div>
  );
};

export default MerchantAgentIntroductionStep;
