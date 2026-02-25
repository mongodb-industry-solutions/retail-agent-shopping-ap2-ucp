export const introSlides = [
  {
    title: "Unlocking the Agentic Commerce Opportunity",
    description:
        `<br/>
        <p>Digital commerce has evolved. We are entering the <b>Agent Economy</b>, where <b>AI assistants</b> do more than search—they autonomously negotiate, assemble carts, and purchase on our behalf, maximizing our convenience and shopping options.</p>
        <br/>
        <p>But this leap forward breaks today's payment systems, which assume a human is actually present to click 'buy'. This shift introduces critical new challenges around <b style="color:#00a35c">trust, authorization, and accountability</b>.</p>
        <br/>
        <p><b>How do we secure a transaction when the buyer is a bot?</b></p>`,
    imagePlaceholder: "Interactive shopping interface mockup",
    imageURL: "/GuidedIntro/agentic-commerce.svg",
  },
  {
    title: "The Trust Layer for Agentic Payments",
    description:
        `<br/>
        <p>To secure bot-led transactions, we must engineer a completely new <b>trust layer</b>. We need absolute certainty in areas like:</p>
        <br/>
        <ul>        
          <li><b>Authorization &#8594; </b> Did the user actually grant permission?</li>
          <li><b>Authenticity &#8594; </b> Is the intent real, or an AI hallucination?</li>
          <li><b>Accountability &#8594; </b> Who is ultimately responsible?</li>
        </ul>
        <br/>
        <p>The <b style="color:#00a35c">Agent Payments Protocol (AP2)</b>, introduced by Google, resolves the critical ambiguities. Using verifiable digital credentials (VDCs) to guarantee every purchase is explicitly approved, secure, and fully auditable.</p>
        <br/>
        <p>AP2 paves the way for a competitive and innovative marketplace.</p>`,
    imagePlaceholder: "Personalized product grid display",
    imageURL: "/GuidedIntro/ap2-trust.svg",
  },
  {
    title: "The Emerging Agentic Stack: UCP + AP2",
       description:
         `<br/>
         <p>To complete an autonomous transaction, <b>AI agents</b> need to both find the product and buy it securely.</p>
         <br/>
         <p>While the <b>Universal Commerce Protocol (UCP)</b> acts as the "common language" allowing agents to discover catalogs and navigate checkouts, <b>AP2</b> is the security layer that AP2 is the security layer that provides the cryptographic proof of authorization.</p>
         <br/>
         <p>Though our demo focuses on <b>AP2’s secure transaction mechanics</b>, they are designed to work together seamlessly.</p>
         <br/>
         <p style="color:#00a35c"><b>UCP orchestrates the shopping journey, and AP2 anchors the payment in trust.</b></p>`,
    imagePlaceholder: "Secure payment flow demonstration",
    imageURL: "/GuidedIntro/ucp-ap2.svg",
  },
  {
    title: "The Mandate Ledger: Anchoring Agentic Trust",
    description:
      `<br/>
      <p>In <b>AP2</b>, trust relies on <b>mandates</b> (Intent, Cart, and Payment). These signed cryptographic records capture exactly what an agent is authorized to execute. But for true accountability, these rules must be permanently preserved.</p>
      <br/>
      <p>Enter the <b>Mandate Ledger</b>, powered by <b>MongoDB</b>. It serves as a secure, tamper-evident audit trail that transforms these signed credentials into durable evidence.</p>
      <br/>
      <p style="">By recording every mandate as a permanent entry, it ensures complete transparency and defensibility for every autonomous transaction.</p>`,
    imagePlaceholder: "Secure payment flow demonstration",
    imageURL: "/GuidedIntro/mandateLedgerArchietcture.svg",
  },
  {
    title: "Let’s Jump into the Shopping Experience of the Future",
    description:
      `<br/>
      <p>Through three different <b>buyer profiles</b>, you will progressively explore how <b>agent-to-agent commerce</b> actually operates, and what it takes to make it trustworthy.</p>
      <br/>
      <p >Each scenario reveals a deeper layer of the emerging stack.</p>
      <br/>
      <p style="">More importantly, you’ll see how <b style="color:#00a35c">the Mandate Ledger Service, powered by MongoDB, acts as the control layer </b>behind the scenes enforcing immutability, preventing tampering, validating access, and preserving a complete, auditable chain of events.</p>`,
    imagePlaceholder: "Secure payment flow demonstration",
    imageURL: "/GuidedIntro/start-demo.svg",
  },
];

export const profiles = [
  {
    id: "straightforward",
    name: "The Straightforward Buyer",
    characteristic: "Efficient & Decisive",
    experienceType: "Happy Path",
    description:
      "A customer who knows what they want, and completes purchases without complications.",
    avatar: "/profiles/straightforward.jpg",
    color: "primary",
    detailedInfo:
      "Objective: Introduce all agents involved in a purchase and how they communicate.",
    profileIcon:  "Checkmark"
  },
  {
    id: "hunter",
    name: "The Hunter Buyer",
    characteristic: "Deal Seeker",
    experienceType: "Looking for Advantages",
    description:
      "A savvy shopper who hunts for deals, and tries to maximize value from every purchase.",
    avatar: "/profiles/hunter.jpg",
    color: "accent",
    detailedInfo:
      "Objective: Introduce the Mandate Service Layer and Role-Based Access Control (RBAC).",
    profileIcon: "CreditCard"
  },
  {
    id: "disputing",
    name: "The Disputing Customer",
    characteristic: "Post-Purchase Advocate",
    experienceType: "Dispute Resolution",
    description:
      "A customer who navigates post-purchase issues and the complaint resolution process.",
    avatar: "/profiles/disputing.jpg",
    color: "accent",
    detailedInfo:
      "Objective: Demonstrate immutability and audit trail capabilities for AP2/UCP compliance.",
    profileIcon: "Warning"
  },
];