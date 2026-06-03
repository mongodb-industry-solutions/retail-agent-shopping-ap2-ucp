import React from 'react'
import ImageContainer from "../ImageContainer";
import { H1 } from "@leafygreen-ui/typography";
import { AGENT_ROLE } from '@/lib/const/bubbleDetails';

const ImmutabilityAndRbacProtectionsStep = ({ type }) => {
  if (type === AGENT_ROLE) return (
    <div>
      <H1 className="text-center">Immutability and RBAC protections</H1>
      
      <ImageContainer
        src="/BehindTheScenes/disputing/ImmutabilityAndRbacProtectionsStep_01.svg"
        alt="Immutability and RBAC Protections"
      />
      
      <div className="info">
        <p>
          The <span className="blue-text">Mandate Ledger Service</span> is designed to preserve transaction history as trusted evidence. That means records are not only signed and auditable, but also protected against unauthorized change.
        </p>
        
        <p>
          When an attempt is made to update or delete a signed transaction record, the system rejects it. This is not just a technical limitation. It is a core design principle of the ledger. Once a mandate is recorded, it becomes part of an append-only audit trail that remains intact.
        </p>
        
        <p>
          <strong>RBAC</strong> adds another layer of protection. <strong>Agents only have the permissions required for their role</strong>. The <span className="blue-text">Auditor Agent</span> can inspect and verify records, but it cannot add, modify or delete them. This separation of responsibilities helps prevent misuse and reinforces trust in the audit trail.
        </p>
        
        <p>
          Together, immutability and role-based access control ensure that transaction history remains complete, tamper-resistant, and reliable for dispute resolution, compliance, and fraud prevention.
        </p>
      </div>
    </div>
  )
}

export default ImmutabilityAndRbacProtectionsStep