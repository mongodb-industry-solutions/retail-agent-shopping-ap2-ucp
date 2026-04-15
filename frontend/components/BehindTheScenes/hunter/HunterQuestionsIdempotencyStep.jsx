import React from 'react';
import { AGENT_ROLE } from "@/lib/const/bubbleDetails";
import ImageContainer from "../ImageContainer";
import { H1, H2, H3, Body } from "@leafygreen-ui/typography";

const HunterQuestionsIdempotencyStep = ({ type }) => {
  if (type === AGENT_ROLE)
    return (
      <div>
        <H1 className="text-center">ONE EXECUTION. ONE RECORD. NO MATTER HOW MANY TIMES IT'S ATTEMPTED.</H1>
        
        <div className="info">
          <p>
            A natural question comes up: could the same operation be executed twice?
          </p>
          <p>
            The answer should be no — and the reason is idempotency.
          </p>
          <p>
            Idempotency means that even if the same operation is attempted multiple times, it only produces one effective result. Without it, retries could create duplicate mandates, duplicate payments, or duplicate records. With it, later attempts return the same result instead of executing again.
          </p>
          <p>
            Here we are showing it through a payment example, but the same guarantee applies across all the mandates and transactions stored throughout the AP2 flow.
          </p>
        </div>

        <ImageContainer
          src="/BehindTheScenes/hunter/HunterQuestionsIdempotencyStep_01.svg"
          alt="One Execution One Record"
          w={700}
          h={600}
        />

        <div className="info">
          <p>
            That is why the Mandate Ledger Service enforces idempotency alongside immutability. Before writing anything to MongoDB Atlas, it checks whether the same mandate has already been processed. If it has, it returns the existing record instead of creating a new one.
          </p>
          <p>
            The result is simple: one mandate, one effective execution, one record.
          </p>
        </div>
      </div>
    );
  else return null;
};

export default HunterQuestionsIdempotencyStep