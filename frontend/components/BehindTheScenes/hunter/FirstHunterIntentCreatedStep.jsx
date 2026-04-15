import React, { useEffect, useState } from "react";
import { AGENT_ROLE } from "@/lib/const/bubbleDetails";
import ImageContainer from "../ImageContainer";
import { Code, Panel } from "@leafygreen-ui/code";
import { H1, H2, H3, Body } from "@leafygreen-ui/typography";
import { journeys } from "@/lib/const/ux-writing";
import { getIntentMandateAPI } from "@/lib/mongo-apis";
import { useSelector } from "react-redux";

const FirstHunterIntentCreatedStep = ({ type }) => {
  const [loadingIntentMandate, setLoadingIntentMandate] = useState(false);
  
  const intentMandate = useSelector(
    (state) =>
      state.MandateLedger.journeysStatus[journeys.hunter.id].intentMandate,
  );

  useEffect(() => {
    if (!intentMandate && !loadingIntentMandate) {
      setLoadingIntentMandate(true);
      getIntentMandateAPI(journeys.hunter.id).finally(() =>
        setLoadingIntentMandate(false),
      );
    }
  }, []);
  
  if (type === AGENT_ROLE)
    return (
      <div>
        <H1 className="text-center">THE DIGITAL CONTRACT</H1>

        <div className="info">
          <p>
            In AP2, a confirmed purchase intent is not just loose application
            data. It becomes a <strong>digital contract</strong> — a structured,
            signed object that captures what the user approved, under which
            conditions, and in which transaction context. Instead of relying on
            probabilistic AI outputs, it provides{" "}
            <a
              href="https://ucp.dev/documentation/ucp-and-ap2"
              target="_blank"
              rel="noopener noreferrer"
            >
              deterministic evidence
            </a>
            .
          </p>
          <p>
            That signature is not just attached to the mandate like a note on
            the side. It is created from a mathematical representation of the
            mandate content, so the approval is bound to the exact data being
            signed. Because{" "}
            <a
              href="https://ucp.dev/2026-01-23/specification/ap2-mandates/"
              target="_blank"
              rel="noopener noreferrer"
            >
              AP2 uses Verifiable Digital Credentials
            </a>{" "}
            with key binding, that approval cannot simply be recreated by
            another party. Other participants in the flow can verify the
            integrity of the mandate and the source of the approval.
          </p>
        </div>

        <ImageContainer
          src="/BehindTheScenes/hunter/FirstHunterIntentCreatedStep_01.svg"
          alt="Digital Contract Creation"
          w={700}
          h={600}
        />

        <div className="info">
          <p>
            The signed mandate is what moves between participants, gets stored,
            and serves as evidence. This matters especially for deferred
            purchases, where a signed Intent Mandate can authorize an agent to
            act later under pre-approved conditions. Because that approval is
            cryptographically bound to both the mandate content and the signer,
            it becomes non-repudiable evidence of what was approved. At
            checkout, AP2 extends the same guarantee by requiring cryptographic
            proof for that specific checkout state.
          </p>
        </div>

        <H2 className="text-center">
          Why MongoDB's document model is a strong fit for mandates
        </H2>

        <H3 className="text-center">
          Preserves the contract as one auditable unit
        </H3>
        <div className="info">
          <p>
            What gets signed is a complete logical payload, not an isolated row.
            MongoDB allows the full mandate, its signatures, verification
            metadata, and audit context to be stored together as one document,
            preserving the contract in the same form in which it is signed,
            exchanged, and later verified.
          </p>
        </div>

        <ImageContainer
          src="/BehindTheScenes/hunter/FirstHunterIntentCreatedStep_02.svg"
          alt="Contract Preservation"
          w={700}
          h={600}
        />

        <H3 className="text-center">
          Simplifies retrieval, verification, and audit
        </H3>
        <div className="info">
          <p>
            Mandates may need to be retrieved later as evidence, revalidated, or
            inspected during disputes. Reading the signed object as a whole is
            simpler than reconstructing it from fragments spread across multiple
            tables and joins.
          </p>
          <p>
            The core issue is that the EdDSA signature was generated from the
            hash of one exact JSON document, serialized in a specific way. If
            that mandate is later split across relational tables, verifying the
            signature requires reconstructing the original JSON through joins,
            reserializing it, and applying canonicalization correctly. Each of
            those steps introduces risk: a missing field, different array order,
            serialization difference, or type change can produce different
            bytes, a different hash, and a failed verification, even if the data
            is logically the same. That is why storing the mandate as one
            complete document is much safer for preserving signature integrity
            over time.
          </p>
        </div>

        <ImageContainer
          src="/BehindTheScenes/hunter/FirstHunterIntentCreatedStep_03.svg"
          alt="Simplified Verification"
          w={700}
          h={600}
        />

        <H3 className="text-center">Supports evolving mandate structures</H3>
        <div className="info">
          <p>
            As mandates expand to include new fields, additional signatures,
            richer metadata, or future AP2 extensions, the document model adapts
            naturally without forcing the schema to be constantly reshaped.
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
          panel={<Panel title="Intent Created" />}
        >
          {JSON.stringify(intentMandate, null, 2)}
        </Code>
        <br></br>
      </div>
    );
  else return null;
};

export default FirstHunterIntentCreatedStep;
