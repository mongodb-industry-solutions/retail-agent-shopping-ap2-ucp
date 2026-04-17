import React from 'react';
import { AGENT_ROLE } from "@/lib/const/bubbleDetails";
import ImageContainer from "../ImageContainer";
import { H1, H2 } from "@leafygreen-ui/typography";
import { Banner } from "@leafygreen-ui/banner";

const WhySignaturesMatterStep = ({ type }) => {
  if (type === AGENT_ROLE)
    return (
      <div>
        <H1 className="text-center">How is trust proven, not assumed?</H1>

        <ImageContainer
          src="/BehindTheScenes/disputing/WhySignaturesMatterStep_01.svg"
          alt="How trust is proven, not assumed"
          w={700}
          h={600}
        />

        <div className="info">
          <p>
            When a mandate is created, <strong>the first thing we must protect is its exact content</strong>. If this is a digital contract, we need proof that the requested item, the offered price, or the agreed terms were exactly those values and not something else.
          </p>
          <p>
            To do that, the mandate contents are transformed into a <strong>unique mathematical fingerprint: a hash</strong>.
          </p>
          <p>
            That hash is calculated from the exact mandate data. Even the smallest change in the contents would produce a completely different hash.
          </p>
        </div>

        <Banner variant="info" className="mb-3" style={{ fontSize: "16px" }}>
          This is what makes the mandate <strong>tamper-evident</strong>: if someone changes the item, price, address, or refund terms later, the hash no longer matches the original content.
        </Banner>

        <ImageContainer
          src="/BehindTheScenes/disputing/WhySignaturesMatterStep_02.svg"
          alt="Cryptographic signing process"
          w={700}
          h={600}
        />

        <div className="info">
          <p>
            Once the mandate content is sealed with its unique fingerprint, each agent signs that same fixed version using its own <strong>cryptographic method</strong>.
          </p>
          <p>
            In this example, the <span className="purple-text">Shopping Agent</span> uses <strong>EdDSA to sign from the buyer side</strong>, while the <span className="green-text">Merchant Agent</span> uses <strong>JWT · RS256 to sign from the seller's side</strong>.
          </p>
          <p>
            The methods differ, but the purpose is the same: to attach approval to the exact mandate version already protected by the hash.
          </p>
          <p>
            What changes between them is the role of the signer and the signing format used to represent that approval.
          </p>
        </div>

        <ImageContainer
          src="/BehindTheScenes/disputing/WhySignaturesMatterStep_03.svg"
          alt="Independent verification process"
          w={700}
          h={600}
        />

        <div className="info">
          <H2>How can approval be independently verified?</H2>
          <p>
            That verification works through a <strong>paired-key model</strong>. Each agent signs with its private key — a secret only that agent controls — while others verify the signature using the corresponding public key, which can be safely shared.
          </p>
          <p>
            If the mandate content is unchanged and the signature matches the signer's public key, the approval is valid.
          </p>
          <p>
            If the content was altered afterward, or if the signature was not produced by the expected signer, verification fails.
          </p>
        </div>

        <Banner variant="info" className="mb-3" style={{ fontSize: "16px" }}>
          This is how AP2 mandates become verifiable evidence: The hash proves that the content stayed intact, the signature proves who approved it, and public-key verification allows both to be checked independently.
        </Banner>
      </div>
    );
  else return null;
};

export default WhySignaturesMatterStep;
