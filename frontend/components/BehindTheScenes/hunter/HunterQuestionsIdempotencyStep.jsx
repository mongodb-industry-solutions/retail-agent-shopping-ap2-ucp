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
            A natural question arises: could the same operation be executed twice?
          </p>
          <p>
            The answer is no — and the reason is idempotency.
          </p>
          <p>
            Idempotency guarantees that even if the same operation is attempted multiple times, it only produces one effective result. Retries can happen for a number of reasons — a network timeout before the response is received, a connection drop mid-request, or an error that causes the merchant agent to resend the same request automatically. Without idempotency, any of these scenarios could create duplicate mandates, duplicate payments, or duplicate records. With it, repeated attempts return the same result instead of triggering a new execution.
          </p>
        </div>

        <ImageContainer
          src="/BehindTheScenes/hunter/HunterQuestionsIdempotencyStep_01.svg"
          alt="One Execution One Record"
          w={700}
          h={600}
        />

        <div className="info">
          <H2>How idempotency is enforced</H2>
          <p>
            The <span className="blue-text">Mandate Ledger Service</span> enforces idempotency in its <strong>Business Logic Layer</strong>, alongside immutability, validation, and concurrency control.
          </p>
          <p>
            In an agentic commerce flow like AP2, <strong>retries are not an edge case — they are an expected behavior</strong>. The <span className="green-text">Merchant Agent</span> operates autonomously, without human intervention, and will automatically resend a request if it does not receive a timely confirmation. This can happen due to a network timeout, a failure at any layer of the service, or a delayed response during a <span className="blue-text">UCP</span> checkout flow.
          </p>
          <p>
            On the <span className="green-text">Merchant Agent</span> side, every write request includes an <strong>X-Idempotency-Key</strong> — a unique identifier that allows the system to track and recognize the request across retries.
          </p>
          <p>
            On the <span className="blue-text">Mandate Ledger Service</span> side, before writing anything to <span className="green-text">MongoDB</span>, it checks whether the request has already been processed by looking it up in a special <span className="green-text">MongoDB</span> collection used to track idempotency:
          </p>
          <ul>
            <li><strong>If the key exists</strong>, the service returns the cached response immediately, without re-processing the request.</li>
            <li><strong>If the key does not exist</strong>, the service processes the request, writes the result to <span className="green-text">MongoDB</span>, and associates the response with that key for future lookups.</li>
          </ul>
          <p>
            To prevent indefinite storage of idempotency records, <strong><a href="https://www.mongodb.com/docs/manual/core/index-ttl/" target="_blank" rel="noopener noreferrer"><span className="green-text">MongoDB</span> TTL indexes</a></strong> automatically expire and delete entries older than 24 hours — keeping storage efficient and data fresh.
          </p>
          <p>
            In <span className="blue-text">UCP</span> checkout flows specifically, <strong>deterministic key generation</strong> is used: the same request always maps to the same unique key, eliminating the risk of duplicate ledger writes during retries.
          </p>
          <p>
            By using this strategy, retries have no side effects, maintain system consistency, and improve user experience. <span className="green-text">MongoDB</span> plays a key role in making this implementation scalable and efficient.
          </p>
        </div>
      </div>
    );
  else return null;
};

export default HunterQuestionsIdempotencyStep