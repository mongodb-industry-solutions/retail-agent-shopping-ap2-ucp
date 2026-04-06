import { AGENT_ROLE } from "@/lib/const/bubbleDetails";
import React from "react";
import ImageContainer from "../ImageContainer";
import { Code, Panel } from "@leafygreen-ui/code";

const CartMandateSignedPaymentCredentialsStep = ({ type }) => {
  if (type === AGENT_ROLE)
    return (
      <div>
        <ImageContainer
          src="/BehindTheScenes/straightforward/CartMandateSignedPaymentCredentialsStep_01.svg"
          alt="Mandate Signed and Payment Credentials Exchanged"
        />
        <div className="info">
          <p>
            As part of the AP2 protocol, the{" "}
            <span className="purple-text">Shopping Agent</span> sends a{" "}
            <strong>signed Cart Mandate</strong> on behalf of the user,
            including all required shipping details, to the Merchant Agent,
            which securely stores it in{" "}
            <span className="green-text">MongoDB</span> via the{" "}
            <span className="green-text">Mandate Ledger Service</span> for audit
            and trust.{" "}
          </p>
        </div>
        <Code
          style={{ borderRadius: "0px" }}
          copyable="true"
          showLineNumbers
          expandable
          darkMode={true}
          language="json"
          collapsedLines={21}
          highlightLines={[]}
          panel={<Panel title="Cart Mandate" />}
        ></Code>
        <div className="info">
          <p>
            Now the <span className="purple-text">Shopping Agent</span> requests
            tokenized payment credentials from the corresponding{" "}
            <span className="yellow-text">Credential Provider Agent</span> to
            complete the purchase with the{" "}
            <span className="green-text">Merchant Agent</span>.
          </p>
        </div>
        <ImageContainer
          src="/BehindTheScenes/straightforward/CartMandateSignedPaymentCredentialsStep_02.svg"
          alt="Payment Token"
        />
      </div>
    );
  else return null;
};

export default CartMandateSignedPaymentCredentialsStep;
