import React from "react";
import ImageContainer from "../ImageContainer";

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
          Mandate — one of the core building blocks of the AP2 protocol.
        </p>
      </div>
      <div className="d-flex flex-column gap-4">
        <ImageContainer
          src="/BehindTheScenes/straightforward/MerchantAgentIntroductionStep_02.svg"
          alt="Meet Cryptographic Mandates"
        />
        <ImageContainer
          className="mt-4"
          src="/BehindTheScenes/straightforward/MerchantAgentIntroductionStep_03.svg"
          alt="Meet Mandate Communication"
        />
      </div>
      <div className="info">
        <p>
          Before sending it, the <span className="purple-text">Shopping Agent</span> signs the <strong>Intent Mandate</strong> using
          its credentials, as required by the <strong>AP2 protocol</strong>, to generate
          verifiable proof of the user’s explicit intent. In this way, it is no
          longer just a simple message but becomes a verifiable instruction that
          the <span className="green-text">Merchant Agent</span> can validate and securely store for future audits,
          preserving trustworthy evidence of the user’s intent.
        </p>
      </div>
    </div>
  );
};

export default MerchantAgentIntroductionStep;
