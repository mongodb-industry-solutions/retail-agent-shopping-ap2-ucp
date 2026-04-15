import React, { useEffect, useState } from 'react';
import { AGENT_ROLE } from "@/lib/const/bubbleDetails";
import ImageContainer from "../ImageContainer";
import { Code, Panel } from "@leafygreen-ui/code";
import { H1 } from "@leafygreen-ui/typography";
import { journeys } from "@/lib/const/ux-writing";
import { getIntentMandateAPI } from "@/lib/mongo-apis";
import { useSelector } from "react-redux";

export const HunterIntentImmutabilityStep = ({ type }) => {
  const [loadingSecondIntentMandate, setLoadingSecondIntentMandate] = useState(false);
  
  const secondIntentMandate = useSelector(
    (state) =>
      state.MandateLedger.journeysStatus[journeys.hunter.id].intentMandates?.[1],
  );

  useEffect(() => {
    if (!secondIntentMandate && !loadingSecondIntentMandate) {
      setLoadingSecondIntentMandate(true);
      getIntentMandateAPI(journeys.hunter.id, 2).finally(() =>
        setLoadingSecondIntentMandate(false),
      );
    }
  }, []);

  if (type === AGENT_ROLE)
    return (
      <div>
        <H1 className="text-center">CONTRACTS DON'T GET EDITED</H1>
        
        <div className="info">
          <p>
            When a user changes their mind after offering a cart, the agent doesn't go back and update the existing mandate. It creates a new one. In this demo, every intent is signed — which means every intent is a sealed contract. And sealed contracts don't get rewritten.
          </p>
          <p>
            But agent behavior alone isn't what enforces this. Even if the Merchant Agent produced an error — or attempted to correct a previously stored mandate — the Mandate Ledger Service would block it.
          </p>
        </div>
        
        <ImageContainer
          src="/BehindTheScenes/hunter/HunterIntentImmutabilityStep_01.svg"
          alt="Contracts Don't Get Edited"
          w={700}
          h={600}
        />
        
        <div className="info">
          <p>
            The Mandate Ledger Service acts as a protective middleware between agents and MongoDB. No agent communicates directly with the database. Every request passes through the service first, and the service enforces three things before any write reaches storage:
          </p>
          <ul>
            <li><strong>Authentication</strong> — API key validation and role-based access control determine what each agent is allowed to do. No agent has update or delete permissions on mandate documents.</li>
            <li><strong>Business logic</strong> — immutability is enforced at this layer. A request to modify or delete an existing mandate is rejected before it ever touches the database.</li>
            <li><strong>Data access</strong> — only valid, append-only writes reach MongoDB, where mandates are stored with Queryable Encryption.</li>
          </ul>
          <p>
            The result is that once a mandate is written, it cannot be changed or removed by any agent or system.
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
          panel={<Panel title="New intent created" />}
        >
          {JSON.stringify(secondIntentMandate, null, 2)}
        </Code>
        <br/>
      </div>
    );
  else return null;
};
