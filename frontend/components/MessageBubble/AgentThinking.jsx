import React from "react";
import styles from "./MessageBubble.module.css";
import { Body, Subtitle } from "@leafygreen-ui/typography";
import Image from "next/image";

const AgentThinking = () => {
  return (
    <div>
      <div className="agentHeader">
        <Image
          src="/icons/ShoppingAgentAP2chatFlow.png"
          alt="Agent headshot"
          width={60}
          height={60}
        />
        <Subtitle className="agentPrefix">Agent's response</Subtitle>
      </div>
      <div className={`speechBubble answerBubble ${styles.thinkingBubble}`}>
        <Body
          className={`messageContent ${styles.thinkingMessage} ${styles.pulse}`}
        >
          Agent is thinking...
          <span className={styles.dots}>...</span>
        </Body>
      </div>
    </div>
  );
};

export default AgentThinking;
