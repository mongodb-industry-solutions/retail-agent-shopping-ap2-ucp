import { AGENT_ROLE } from "@/lib/const/bubbleDetails";
import React, { useState, useEffect } from "react";
import ImageContainer from "../ImageContainer";
import { Code, Panel } from "@leafygreen-ui/code";
import { getCartMandatesWithTwoSignatures } from "@/lib/mongo-apis";
import { useSelector } from "react-redux";
import { journeys } from "@/lib/const/ux-writing";

const CartMandateSignedPaymentCredentialsStep = ({ type }) => {
  const [loadingMandates, setLoadingMandates] = useState(false);
  const cartMandateWithTwoSignatures = useSelector(
    (state) =>
      state.MandateLedger.journeysStatus[journeys.straightforward.id]
        .cartMandateWithTwoSignatures,
  );

  useEffect(() => {
    if (cartMandateWithTwoSignatures == null && !loadingMandates) {
      setLoadingMandates(true);
      getCartMandatesWithTwoSignatures(journeys.straightforward.id).finally(
        () => setLoadingMandates(false),
      );
    }
  }, []);

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
            <strong>signed Cart Mandate</strong> on behalf of the user,{" "}
            including all required shipping details, to the{" "}
            <span className="green-text">Merchant Agent</span>. 
          </p>
        </div>
        <div className="info">
          <p>
            The Merchant signs the cart to commit to fulfilling the order, without having access to the user's full conversation with the <span className="purple-text">Shopping Agent</span>. The Cart Mandate is then securely stored in <span className="green-text">MongoDB</span> via the <span className="green-text">Mandate Ledger Service</span> for audit and trust.
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
          panel={<Panel title="Cart Mandate Signed by Shopping and Merchant Agent" />}
        >
          {JSON.stringify(cartMandateWithTwoSignatures, null, 2)}
        </Code>
        <div className="info">
          <p>
            Now the <span className="purple-text">Shopping Agent</span> requests
            tokenized payment credentials from the corresponding{" "}
            <span className="yellow-text">Credential Provider Agent</span>. It never sees card numbers. The <span className="yellow-text">Credential Provider Agent</span> manages payment methods securely, but doesn't know what you're buying in detail. The Merchant commits to fulfillment, but does not access raw payment credentials directly.
          </p>
          <p>
            Each agent operating through AP2 has strictly scoped access, adhering to the principle of least privilege and enforcing role-based data isolation as a core security principle.
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
