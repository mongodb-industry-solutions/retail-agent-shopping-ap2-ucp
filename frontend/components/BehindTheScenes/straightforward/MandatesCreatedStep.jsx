import { AGENT_ROLE } from "@/lib/const/bubbleDetails";
import React from "react";
import ImageContainer from "../ImageContainer";
import { Code, Panel } from "@leafygreen-ui/code";

const MandatesCreatedStep = ({ type }) => {
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
        ></Code>
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
        <Code
          style={{ borderRadius: "0px" }}
          copyable="true"
          showLineNumbers
          expandable
          darkMode={true}
          language="json"
          collapsedLines={21}
          highlightLines={[]}
          panel={<Panel title="Cart Mandate 1" />}
        ></Code>
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
          panel={<Panel title="Cart Mandate 2" />}
        ></Code>
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
          panel={<Panel title="Cart Mandate 3" />}
        ></Code>
      </div>
    );
  else return null;
};

export default MandatesCreatedStep;
