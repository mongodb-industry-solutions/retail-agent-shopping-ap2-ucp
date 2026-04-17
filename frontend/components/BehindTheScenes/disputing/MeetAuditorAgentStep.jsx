import React from 'react'
import ImageContainer from "../ImageContainer";
import { H1 } from "@leafygreen-ui/typography";
import { AGENT_ROLE } from '@/lib/const/bubbleDetails';

const MeetAuditorAgentStep = ({ type }) => {
  if (type === AGENT_ROLE) return (
    <div>
      <H1 className="text-center">Meet the Auditor Agent</H1>
      
      <ImageContainer
        src="/BehindTheScenes/disputing/MeetAuditorAgentStep_01.svg"
        alt="Meet Auditor Agent"
         w={700} h={600}
      />
      
      <div className="info">
        <p>
          The <span className="blue-text">Auditor Agent</span> is a specialized agent inside the merchant ecosystem. It communicates with the <span className="purple-text">Shopping Agent</span> when a completed transaction needs to be challenged, reviewed, or verified.
        </p>
        
        <p>
          Unlike the <span className="green-text">Merchant Agent</span>, it does not help execute the purchase. Its role begins after the transaction is complete. With restricted access to the <span className="blue-text">Mandate Ledger Service</span>, it can verify payments, retrieve the full audit trail, and inspect immutable ledger records, but it cannot alter or delete them.
        </p>
        
        <p>
          This is where the concepts introduced progressively throughout the earlier purchase flows come together in action. In a shopping experience that stays entirely inside the <span className="purple-text">Shopping Agent</span>, disputes cannot be resolved through chat history alone. They require signed, structured, and auditable evidence.
        </p>
        
        <p>
          That is why <strong>AP2</strong>, the <span className="blue-text">Mandate Ledger Service</span>, and <span className="green-text">MongoDB</span> are so important in this flow. Together, they make it possible to resolve disputes with trusted transaction records for both the merchant and the user.
        </p>
      </div>
    </div>
  )
}

export default MeetAuditorAgentStep