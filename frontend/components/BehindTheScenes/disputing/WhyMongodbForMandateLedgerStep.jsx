import React from 'react'
import ImageContainer from "../ImageContainer";
import { H1 } from "@leafygreen-ui/typography";
import { AGENT_ROLE } from '@/lib/const/bubbleDetails';

const WhyMongodbForMandateLedgerStep = ({ type }) => {
  if (type === AGENT_ROLE) return (
    <div>
      <H1 className="text-center">Why is MongoDB the ideal foundation?</H1>
      
      <ImageContainer
        src="/BehindTheScenes/disputing/WhyMongodbForMandateLedgerStep_01.svg"
        alt="Why MongoDB for Mandate Ledger"
      />
      
      <div className="info">
        <p>
          At this point, the user has seen the dispute resolved through verifiable evidence: signed mandates, a complete audit trail, and immutable records linked to the payment and transaction history. But that level of trust depends not only on the protocol. It also depends on the <strong>data foundation</strong> behind it.
        </p>
        
        <p>
          As we move deeper into the agentic era, more and more experiences will happen without leaving a trusted AI assistant, including shopping. In that world, data adaptability, security, and performance become essential. These new workloads require a foundation that can <strong>support evolving agent interactions, secure transaction records, and real-time verification at scale</strong>.
        </p>
        
        <p>
          That is why <span className="green-text">MongoDB</span> matters here. It is not just where the mandates are stored. It is the intelligence data layer that helps make these flows practical, auditable, and scalable for the real world.
        </p>
      </div>
    </div>
  )
}

export default WhyMongodbForMandateLedgerStep