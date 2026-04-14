import React, {useState, useEffect} from "react";
import { useSelector } from "react-redux";
import { AGENT_ROLE } from "@/lib/const/bubbleDetails";
import ImageContainer from "../ImageContainer";
import { Code, Panel } from "@leafygreen-ui/code";
import { getPaymentDocument } from "@/lib/mongo-apis";
import { journeys } from "@/lib/const/ux-writing";

const PaymentCompletedStep = ({ type }) => {
    const [loadingPaymentDocument, setLoadingPaymentDocument] = useState(false);
  const paymentDocument = useSelector(
    (state) =>
      state.MandateLedger.journeysStatus[journeys.straightforward.id]
        .paymentDocument,
  );
    const paymentMandate = useSelector(
    (state) =>
      state.MandateLedger.journeysStatus[journeys.straightforward.id]
        .paymentMandate,
  );

  useEffect(() => {
    if (paymentDocument == null && !loadingPaymentDocument) {
      setLoadingPaymentDocument(true);
      getPaymentDocument(journeys.straightforward.id).finally(
        () => setLoadingPaymentDocument(false),
      );
    }
  }, []);
  if (type === AGENT_ROLE)
    return (
      <div>
        <div className="info">
          <p>
            The payment is successful. The completed transaction is then
            recorded in <span className="green-text">MongoDB</span> through the{" "}
            <span className="green-text">Mandate Ledger Service</span>, creating
            a secure, reliable, and fully auditable record for the merchant.
            Under the <strong>AP2</strong> protocol, this record captures the{" "}
            <strong>Intent, Cart, and Payment Mandates</strong>, including their{" "}
            <strong>cryptographic signatures</strong> and the associated{" "}
            <strong>transaction data</strong>.
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
          panel={<Panel title="Payment" />}
        >
          {JSON.stringify(paymentDocument, null, 2)}
        </Code>
        <br></br>
        <Code
          style={{ borderRadius: "0px" }}
          copyable="true"
          showLineNumbers
          expandable
          darkMode={true}
          language="json"
          collapsedLines={21}
          highlightLines={[]}
          panel={<Panel title="Payment Mandate" />}
        >
          {JSON.stringify(paymentMandate, null, 2)}
        </Code>
        <div className="info">
          <p>
            Finally, the <span className="green-text">Merchant Agent</span>{" "}
            sends the receipt to the{" "}
            <span className="purple-text">Shopping Agent</span>.
          </p>
        </div>
        <ImageContainer
          src="/BehindTheScenes/straightforward/PaymentCompletedStep_01.svg"
          alt="Payment Token"
        />
      </div>
    );
  else return null;
};

export default PaymentCompletedStep;
