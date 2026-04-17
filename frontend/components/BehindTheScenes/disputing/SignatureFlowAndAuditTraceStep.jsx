import React from 'react'
import ImageContainer from "../ImageContainer";
import { H1 } from "@leafygreen-ui/typography";
import { AGENT_ROLE } from '@/lib/const/bubbleDetails';

const SignatureFlowAndAuditTraceStep = ({ type }) => {
  if (type === AGENT_ROLE) return (
    <div>
      <H1 className="text-center">Signature Flow and Audit Trace</H1>
      
      <ImageContainer
        src="/BehindTheScenes/disputing/SignatureFlowAndAuditTraceStep_01.svg"
        alt="Signature Flow and Audit Trace"
      />
      
      <div className="info">
        <p>
          The <span className="blue-text">Auditor Agent</span> can verify a payment by ID, retrieve the complete audit trail, and inspect signed records stored as immutable evidence in the <span className="blue-text">Mandate Ledger Service</span>.
        </p>
        
        <p>
          As shown in the signature sequence diagram, the purchase is recorded step by step through signed <strong>Intent</strong>, <strong>Cart</strong>, and <strong>Payment Mandates</strong>. These signatures preserve what was requested, what was accepted, and what was ultimately paid.
        </p>
        
        <p>
          In <span className="green-text">MongoDB</span>, the payment and transaction records link the mandates associated with that purchase. This allows the <span className="blue-text">Auditor Agent</span> to use a payment_id as the entry point to trace the full history behind it and verify what was agreed at each stage.
        </p>
      </div>
    </div>
  )
}

export default SignatureFlowAndAuditTraceStep