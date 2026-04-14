import { AGENT_ROLE } from "@/lib/const/bubbleDetails";
import React, { useEffect, useState } from "react";
import ImageContainer from "../ImageContainer";
import { Code, Panel } from "@leafygreen-ui/code";
import { getCartMandatesAPI } from "@/lib/mongo-apis";
import { journeys } from "@/lib/const/ux-writing";
import { useSelector } from "react-redux";

const MandatesCreatedStep = ({ type }) => {
  const [loadingMandates, setLoadingMandates] = useState(false);
  const cartMandates = useSelector(
    (state) =>
      state.MandateLedger.journeysStatus[journeys.straightforward.id]
        .cartMandates,
  );

  useEffect(() => {
    if (cartMandates.length === 0 && !loadingMandates) {
      setLoadingMandates(true);
      getCartMandatesAPI(journeys.straightforward.id).finally(() =>
        setLoadingMandates(false),
      );
    }
  }, []);

  if (type === AGENT_ROLE)
    return (
      <div>
        <ImageContainer
          src="/BehindTheScenes/straightforward/MandatesCreatedStep_01.svg"
          alt="Meet Shopping agent"
          w={500}
          h={400}
        />
        <div className="info">
          <p>
            Signing the mandate is only part of the story.
            <br />
            To truly establish trust, it needs to be stored in a way that
            guarantees it can’t be changed.
            <br />
            That’s the role of the{" "}
            <span className="green-text">Mandate Ledger</span>.
          </p>
          <p>
            It acts as a service layer on top of{" "}
            <span className="green-text">MongoDB</span>, ensuring every mandate
            is stored as an immutable document — capturing each step of the
            interaction in a way that is fully traceable, verifiable, and
            auditable over time
          </p>
          <p>
            At this stage, the{" "}
            <span className="green-text">Merchant Agent</span> has stored,
            through the{" "}
            <span className="green-text">Mandate Ledger Service</span>, the
            purchase intent as a mandate cryptographically signed by the{" "}
            <span className="purple-text">Shopping Agent</span> on behalf of the
            user. It is recorded in this way:
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
          panel={<Panel title="Intent Mandate" />}
        >
          {JSON.stringify(
            cartMandates.find((mandate) => mandate.status === "signed"),
            null,
            2,
          )}
        </Code>
        <div className="info">
          <p>
            The <span className="green-text">Merchant Agent</span> generated
            three Cart Mandate options with a “proposed” status, not yet signed
            by the user, and stored them in{" "}
            <span className="green-text">MongoDB</span> via the{" "}
            <strong>Mandate Ledger Service</strong> for future audit.
          </p>
        </div>
        <ImageContainer
          src="/BehindTheScenes/straightforward/MandatesCreatedStep_02.svg"
          alt="Meet Shopping agent"
        />
        {cartMandates
          .filter((mandate) => mandate.status !== "signed")
          .map((mandate, index) => (
            <div key={index}>
              <Code
                style={{ borderRadius: "0px" }}
                copyable="true"
                showLineNumbers
                expandable
                darkMode={true}
                language="json"
                collapsedLines={6}
                highlightLines={[]}
                panel={<Panel title={`Cart Mandate ${index + 1}`} />}
              >
                {JSON.stringify(mandate, null, 2)}
              </Code>
              <br></br>
            </div>
          ))}
      </div>
    );
  else return null;
};

export default MandatesCreatedStep;
